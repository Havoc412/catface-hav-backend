import numpy as np
import cv2

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from catface_hav_v1.app import FaceAnalysis
from catface_hav_v1.consts import FACE_MODE

from DB import FaceEmbeddingDB, SQLiteDB
from Errcode import Ecnn


from .utils import test
def cnn_test(request):
    data = {
        "status": 200,
        "msg": test()
    }
    return JsonResponse(data)

# @csrf_exempt
def detect_cat(request):
    """
    这是一个 1：k 的任务。
    :param request:
    :return:
    """
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            # 将文件内容读取到内存中
            file_content = file.read()
            # 将内存中的文件内容转换为numpy数组，以便cv2可以处理
            nparr = np.frombuffer(file_content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # start Embedding model
            app = FaceAnalysis(verbose=False)
            faces = app.get(img, mode=FACE_MODE.single)

            if len(faces) == 0:
                # todo 关于 msg 的架构设计
                return JsonResponse({'status': Ecnn.NoCatFaceGet, 'message': 'No cat face get.'})
            else:
                face = faces[0]

            # search Milvus
            db = FaceEmbeddingDB()
            results = db.query(face.embedding)
            db.close()

            cats = {}
            for (id, dis) in results:
                if dis > 0.8:  # todo 需要一个合适的阙值
                    print(id, dis)
                    continue
                if id not in cats:
                    cats[id] = {'id': id, 'cnt': 0, 'conf': 0}
                cats[id]['cnt'] += 1
                cats[id]['conf'] += dis

            # 按平均 dis 升序排序
            cats_sorted = sorted(cats.items(), key=lambda x: x[1]['dis'] / x[1]['cnt'])
            print(cats_sorted)
            ids_sorted = []
            dis_sum = 0
            for id, info in cats_sorted:
                ids_sorted.append(id)
                info['dis'] /= info['cnt']
                dis_sum += info['dis']

            def cal_conf(dis):
                if dis == dis_sum or dis == 0:
                    return 97
                return int((1 - dis / dis_sum) * 100)

            print(ids_sorted, cats_sorted)
            # get_full_data
            cat_infor = []
            with SQLiteDB() as db:
                results = db.fetch_by_ids(ids_sorted)
                print(results)
                for result in results:
                    infor = {
                        "id": result[0],
                        "name": result[1],
                        "breed": result[2],
                        "gender": result[3],
                        "conf": cal_conf(cats[ids_sorted[ids_sorted.index(result[0])]]['dis'])
                    }
                    cat_infor.append(infor)
            print(cat_infor)
            cat_infor = sorted(cat_infor, key=lambda x: x['conf'], reverse=True)
            data = {
                "status": 200,
                "cat_infor_list": cat_infor
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'status': 200, 'message': 'No file provided'})
    else:
        return JsonResponse({'status': 200, 'message': 'Invalid request'})

index = 11
def add_cat(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            # 将文件内容读取到内存中
            file_content = file.read()
            # 将内存中的文件内容转换为numpy数组，以便cv2可以处理
            nparr = np.frombuffer(file_content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # start Embedding model
            app = FaceAnalysis(verbose=False)
            faces = app.get(img, mode=FACE_MODE.single)

            if len(faces) == 0:
                return JsonResponse({'status': 200, 'message': 'No cat face get.'})
            else:
                face = faces[0]

            # sql  # todo 直接模拟数据。
            global index
            # with SQLiteDB() as db:
            #     db.insert_animal(index, f"测试新猫{index}", "x", "y")

            # Milvus
            embeddings = [face.embedding]
            labels = [index]
            db = FaceEmbeddingDB()
            results = db.insert(embeddings, labels)
            db.close()
            # index += 1

            cv2.imwrite("./test.jpg", face.img)

            return JsonResponse({'status': 200, 'message': "Add Successfully!"})
        else:
            return JsonResponse({'status': 200, 'message': 'No file provided'})
    else:
        return JsonResponse({'status': 200, 'message': 'Invalid request'})

