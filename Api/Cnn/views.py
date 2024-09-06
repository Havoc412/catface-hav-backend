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
                return JsonResponse({ 'status': 201 })
            else:
                face = faces[0]
            print(face.breed)

            # search Milvus
            db = FaceEmbeddingDB()
            results = db.query(face.normed_embedding)
            db.close()

            cats = {}
            cats_id = []
            for (id, dot) in results:
                if dot < 0.4:  # todo 需要一个合适的阙值
                    print(id, dot)
                    continue
                if id not in cats:
                    cats[id] = {'cnt': 0, 'conf': 0}
                    cats_id.append(id)
                cats[id]['cnt'] += 1
                cats[id]['conf'] += dot

            # check - 2  如果为空，一定条件下获取第一个作为参考
            if len(cats) == 0 and results[0][1] > 0:
                id, dot = results[0]
                cats[id] = {'cnt': 1, 'conf': dot}
                cats_id.append(id)

            def cal_conf(cat, breed):
                """
                结合 embedding 的 conf 和 breed 的 conf 共同计算。
                :param cat:
                :param breed:
                :return:
                """
                breed_conf = face.breed['conf'][face.breed['top5'].index(breed)]
                conf = cat['conf'] / cat['cnt']
                print(breed_conf, breed, conf)
                return int(conf * breed_conf * 100)

            # get_full_data
            cats_infor = []
            with SQLiteDB() as db:
                results = db.fetch_by_ids(cats_id)
                print(results, cats)
                for result in results:
                    if result[4] not in face.breed['top5']:
                        continue
                    conf = cal_conf(cats[id], result[4])
                    if conf == 0:
                        continue
                    id = result[0]
                    infor = {  # todo 之后应该用 model 包装一下。
                        "id": id,
                        "name": result[1],
                        "breed": result[2],
                        "gender": result[3],
                        "conf": conf
                    }
                    cats_infor.append(infor)
            print(cats_infor)
            cats_infor_sorted = sorted(cats_infor, key=lambda x: x['conf'], reverse=True)
            data = {
                "status": 200,
                "cat_infor_list": cats_infor_sorted
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

