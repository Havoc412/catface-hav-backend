import os
import cv2
import numpy as np

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


from catface_hav_v1.app import FaceAnalysis, DBSCAN
from catface_hav_v1.consts import FACE_MODE
from catface_hav_v1.utils import merge_breeds
from Api.models import catInfor, catInforGroup, CatInforSelectMode

from DB import FaceEmbeddingDB, SQLiteDB
from Errcode import Ecnn

from .utils import test, load_temp_file, cal_conf
from utils import trans_breed

def cnn_test(request):
    data = {
        "status": 200,
        "msg": test()
    }
    return JsonResponse(data)

def handle_file_upload(f, u):
    file_directory = './test/'
    import os
    if not os.path.exists(file_directory):
        os.makedirs(file_directory)

    file_path = os.path.join(file_directory, f'{u}_{f.name}')
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path

# @csrf_exempt
@require_POST
def detect_cat(request):
    """
    这是一个 1：k 的任务。
    需要同时处理 image && video，不过 FA 本身就搞定了这一点。
    :param request:
    :return:
    """
    # FILE handle
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'status': 400, 'message': 'No file provided'})
    err, file_res = load_temp_file(file)  # 类似 go 的写法;
    if err:
        return JsonResponse({'status': 400, **file_res})

    # start Embedding model
    data = file_res['data']
    app = FaceAnalysis(root="./catface_hav_v1/model_zoo/models", verbose=False)
    faces = app.get(data, mode=FACE_MODE.single)

    if file_res['tmp_file_created']:
        data.release()  # 释放视频文件
        os.unlink(file_res['tmp_file_path'])  # 删除临时文件

    # handle faces to centers
    """
    center: {
        'embedding': normed,
        'cnt': power,  # cnt 同时也作为 breeds 中 conf 的【二次置信度】
        'breed': { # face.breed,
            'top5': [], # en; maybe more than 5.
            'conf': [],
        } 
    }
    """
    if len(faces) == 0:
        return JsonResponse({ 'status': Ecnn.NoCatFaceGet })
    elif len(faces) == 1:
        face = faces[0]
        centers = [{
            'embedding': face.normed_embedding,
            'cnt': 1,
            'breed': face.breed
        }]
    else:
        dbscan = DBSCAN(eps=.3, verbose=False)
        centers = dbscan.filtrate_embeddings(faces)

    # merge breed
    """
    breed: {
        'top5': [],
        'conf': []
    }
    """
    if len(centers) > 1:
        cnt_sum = 0
        for center in centers:
            cnt_sum += center['cnt']
            for i in range(len(center['breed']['conf'])):
                center['breed']['conf'][i] *= center['cnt']
        breed = merge_breeds([center['breed'] for center in centers], cnt_sum)
    else:
        breed = centers[0]['breed']

    # CAL dot by Milvus
    cats = {}  # 根据 embedding 计算出的 待筛选目标。
    """
    cat: {
        'conf': 
        'cnt': 
    }
    """
    cats_id = set()
    with FaceEmbeddingDB() as db:
        for center in centers:
            results = db.query(center['embedding'])
            flag_save_any = False
            for (id, dot) in results:
                if dot < 0.4:  # todo 需要一个合适的阙值
                    print(id, dot)
                    continue
                if id not in cats_id:
                    if not flag_save_any:
                        flag_save_any = True
                    cats[id] = {'cnt': 0, 'conf': 0}
                    cats_id.add(id)
                cats[id]['cnt'] += 1 * center['cnt']
                cats[id]['conf'] += dot * center['cnt']
            # when not any one get
            if not flag_save_any and results[0][1] > 0:
                id, dot = results[0]
                if id not in cats_id:
                    cats[id] = {'cnt': 0, 'conf': 0}
                    cats_id.add(id)
                cats[id]['cnt'] += 1 * center['cnt']
                cats[id]['conf'] += dot * center['cnt']

    # Search SQLite3 to get basic data  # todo 同时查询 notice
    cats_infor = []
    with SQLiteDB() as db:
        cig = catInforGroup(db)
        ret_cats = cig.select(cats_id, CatInforSelectMode.BASIC)
        del cig  # 单纯当一个媒介

        # filter by breed
        if ret_cats is not None:
            for catinfor in ret_cats:
                if catinfor._breed_en not in breed['top5']:
                    continue
                conf = cal_conf(cats[catinfor._id], catinfor._breed_en, breed)
                if conf > 0:
                    cats_infor.append(catinfor.to_dict_with_conf(conf))
        del ret_cats

    # Check and ret
    if len(cats_infor) > 0:
        cats_infor_sorted = sorted(cats_infor, key=lambda x: x['conf'], reverse=True)
        print(cats_infor_sorted)
        data = {
            "status": 200,
            "breed": trans_breed(breed['top5'][0]),
            "cat_infor_list": cats_infor_sorted
        }
    else:
        data = {
            "status": Ecnn.NoCatMatch,
            "breed": trans_breed(breed['top5'][0])
        }
    return JsonResponse(data)

def add_cat(request):
    if request.method == 'POST':
        # handle data sended
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'status': 400, 'message': 'No file provided'})

        err, file_res = load_temp_file(file)
        if err:
            return JsonResponse({'status': 400, **file_res})

        infor = {
            'name': request.POST.get('name'),
            'gender': request.POST.get('gender'),
            'breed': request.POST.get('breed')  # get [ch] from front
        }
        catinfor = catInfor(**infor)

        # FA detect with DBSCAN
        data = file_res['data']
        frame = None
        if file_res['tmp_file_created']:
            res, frame = data.read()
            if not res:
                print("❌ 读取第一帧失败。")

        app = FaceAnalysis(root="./catface_hav_v1/model_zoo/models", verbose=False)
        faces = app.get(data, mode=FACE_MODE.single)

        if file_res['tmp_file_created']:
            data.release()  # 释放视频文件
            os.unlink(file_res['tmp_file_path'])  # 删除临时文件
            data = frame  # 保持同名，简化后续操作。
            print(type(data))

        # handle faces to centers
        if len(faces) == 0:
            return JsonResponse({'status': Ecnn.NoCatFaceGet})
        elif len(faces) == 1:
            face = faces[0]
            centers = [{
                'embedding': face.normed_embedding,
                'cnt': 1,
                'breed': face.breed  # /add_cat/ 中 breed 没有什么用。
            }]
        else:
            dbscan = DBSCAN(eps=.1, verbose=False)   # 设一个很低的 eps， 过滤基本的重复对象。
            centers = dbscan.filtrate_embeddings(faces)

        # Save to SQLite3
        with SQLiteDB() as db:
            catinfor.insert_sql(db)  # 于是就得到了 ID
            # save avatar
            cv2.imwrite(f"./Api/static/images/cats/{catinfor._id}.jpg", data)

        # save to Milvus
        embeddings = [center['embedding'] for center in centers]
        labels = [catinfor._id] * len(embeddings)
        with FaceEmbeddingDB() as db:
            db.insert(embeddings, labels)

        return JsonResponse({'status': 200, 'message': "Add Successfully!", 'data': catinfor._id})
    else:
        return JsonResponse({'status': 200, 'message': 'Invalid request'})

