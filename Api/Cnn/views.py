import os
import cv2
import numpy as np

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from catface_hav_v1.app import FaceAnalysis, DBSCAN
from catface_hav_v1.consts import FACE_MODE
from catface_hav_v1.utils import merge_breeds

# TODO 重构一下；采取 model 的前缀，以便代码的识别。
from Api import models as ApiModels

from DB import FaceEmbeddingDB, SQLiteDB, MySQLDB
from Errcode import Ecnn

from .utils import test, load_temp_file, cal_conf, handle_file_upload
from utils import trans_breed


def cnn_test(request):
    data = {
        "code": 200,
        "msg": test()
    }
    return JsonResponse(data)


# @csrf_exempt
@require_POST
def detect_cat(request):
    """
    这是一个 1：k 的任务。
    需要同时处理 image && video，不过 FA 本身就搞定了这一点。
    :param request:
    :return:
    """
    # STAGE 1. FILE handle
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'code': 400, 'message': 'No file provided'})
    err, file_res = load_temp_file(file)  # 类似 go 的写法;  # TODO 如果在同一台机器上，go 或许也能直接访问到。
    if err:
        return JsonResponse({'code': 400, **file_res})

    # STAGE 2.1 Start Embedding model；帧·特征提取
    data = file_res['data']
    app = FaceAnalysis(root="./catface_hav_v1/model_zoo/models", verbose=False)
    faces = app.get(data, mode=FACE_MODE.single)

    if file_res['tmp_file_created']:
        data.release()  # 释放视频文件
        os.unlink(file_res['tmp_file_path'])  # 删除临时文件

    # STAGE 2.2 Handle faces to centers；聚类
    """ MODEL
    center: {
        'embedding': normed,
        'cnt': power,  # cnt 同时也作为 breeds 中 conf 的【二次置信度】 实现上采取 累乘 的方案。
        'breed': { # face.breed,
            'top5': [], # en; maybe more than 5.
            'conf': [],
        } 
    }
    """
    if len(faces) == 0:
        return JsonResponse({'code': Ecnn.NoCatFaceGet})
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

    # STAGE 2.3 Merge Breed
    """ MODLE
    breed: {
        'top5': [v1, ..., v5],
        'conf': [p1, ..., p5]
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

    # STAGE 3 CAL dot by Milvus  # TODO 迁移到 ES. Reason Server 内存有限。
    """ MODEL
    cat: {
        'conf': 
        'cnt': 
    }
    """
    cats = {}  # 根据 embedding 计算出的 待筛选目标。
    cats_id = set()
    with FaceEmbeddingDB() as db:
        for center in centers:
            results = db.query(center['embedding'])
            flag_save_any = False
            for (id, dot) in results:
                if dot < 0.4:  # todo 需要一个合适的阙值
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

    # STAGE 获取 cats_infor 并用 breed 计算 conf
    animalManager = None
    cats_infor = []
    with MySQLDB() as db:
        animalManager = ApiModels.AnimalManager(db)
        animals = animalManager.selectByID(cats_id, ApiModels.AnimalSelectMode.BASIC)
        # filter by breed
        cats_id.clear()
        if animals is not None:
            for animal in animals:
                anm_facebreed = animal.getFaceBreedMap()
                if anm_facebreed is None:
                    continue
                conf = cal_conf(cats[animal._id], anm_facebreed, breed)
                if conf > 0:
                    cats_infor.append(animal.to_dict_with_conf(conf))  # 将计算出来的 conf 和基本信息整合起来。
                    cats_id.add(animal._id)
        del animals

    # # v2 face_breed top3  # Droped
    # cats_fb_conf = []  # [{ id: xx, conf: 0.xx }, ...]
    # with MySQLDB() as db:
    #     afbGroup = models.AnmFaceBreedGroup(db)
    #     ret_cats = afbGroup.select(cats_id)
    #     cats_id.clear()  # QUESTION
    #     if ret_cats is not None:
    #         for singleFaceBreed in ret_cats:  # INFO 原本是 5: 1，现在是 5: 3，计算方式自然不同
    #             id_conf = singleFaceBreed.calTargetFaceBreedProbWithID(breed)
    #             if id_conf['conf'] > 0:
    #                 cats_fb_conf.append(id_conf)
    #                 cats_id.add(id_conf['id'])

    # STAGE 4 Check and ret
    print(cats_infor)
    if len(cats_infor) > 0:
        # search SQLite3 to get notice
        notices = []
        # if len(cats_id) > 0:
        #     # TODO 还是需要迁移过去。
        #     with SQLiteDB() as db:
        #         ng = noticeGroup(db)
        #         results = ng.select(cats_id)
        #         del ng
        #         if results is not None:
        #             for notice in results:
        #                 notices.append(notice.to_dict_with_name(cig.get_name_by_id(notice._cat_id)))
        cats_infor_sorted = sorted(cats_infor, key=lambda x: x['conf'], reverse=True)
        print(cats_infor_sorted)
        data = {
            "code": 200,
            "face_breed": trans_breed(breed['top5'][0]),  # INFO CatFace模型参考的 breed 特指 Face。
            "cats_list": cats_infor_sorted,
            "notices": notices
        }
    else:
        data = {
            "code": Ecnn.NoCatMatch,
            "face_breed": trans_breed(breed['top5'][0])  # 给 Vue 作为 body_breed 的参考。
        }
    return JsonResponse(data)


# # TODO 关于图片等资源的保存，同步; IDEA 或许可以通过缓存机制 + redis 同步信息。
# def add_cat(request):
#     if request.method == 'POST':
#         # handle data sended
#         file = request.FILES.get('file')
#         if not file:
#             return JsonResponse({'code': 400, 'message': 'No file provided'})
#
#         err, file_res = load_temp_file(file)
#         if err:
#             return JsonResponse({'code': 400, **file_res})
#
#         infor = {
#             'name': request.POST.get('name'),
#             'sex': request.POST.get('gender'),
#             'breed': request.POST.get('breed')  # get [ch] from front
#         }
#         catinfor = catInfor(**infor)
#
#         # FA detect with DBSCAN
#         data = file_res['data']
#         frame = None
#         if file_res['tmp_file_created']:
#             res, frame = data.read()
#             if not res:
#                 print("❌ 读取第一帧失败。")
#
#         app = FaceAnalysis(root="./catface_hav_v1/model_zoo/models", verbose=False)
#         faces = app.get(data, mode=FACE_MODE.single)
#
#         if file_res['tmp_file_created']:
#             data.release()  # 释放视频文件
#             os.unlink(file_res['tmp_file_path'])  # 删除临时文件
#             data = frame  # 保持同名，简化后续操作。
#             print(type(data))
#
#         # handle faces to centers
#         if len(faces) == 0:
#             return JsonResponse({'code': Ecnn.NoCatFaceGet})
#         elif len(faces) == 1:
#             face = faces[0]
#             centers = [{
#                 'embedding': face.normed_embedding,
#                 'cnt': 1,
#                 'breed': face.breed  # /add_cat/ 中 breed 没有什么用。
#             }]
#         else:
#             dbscan = DBSCAN(eps=.1, verbose=False)  # 设一个很低的 eps， 过滤基本的重复对象。
#             centers = dbscan.filtrate_embeddings(faces)
#
#         # Save to SQLite3
#         with SQLiteDB() as db:
#             catinfor.insert(db)  # 于是就得到了 ID
#             # catinfor.save()
#             # save avatar
#             cv2.imwrite(f"./Api/static/images/cats/{catinfor._id}.jpg", data)
#
#         # save to Milvus
#         embeddings = [center['embedding'] for center in centers]
#         labels = [catinfor._id] * len(embeddings)
#         with FaceEmbeddingDB() as db:
#             db.insert(embeddings, labels)
#
#         return JsonResponse({'code': 200, 'message': "Add Successfully!", 'data': catinfor._id})
#     else:
#         return JsonResponse({'code': 200, 'message': 'Invalid request'})
