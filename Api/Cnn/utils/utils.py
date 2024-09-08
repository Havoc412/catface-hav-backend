import numpy as np
import cv2
from tempfile import NamedTemporaryFile


def test():
    return "Cnn test."

def load_temp_file(file):
    """
    读取缓存文件，并保存状态。（实现方式和请求还挺相似）
    # todo 考虑实现持久化存储作为 Log，同时收集数据。不过还是用 FA 来实现会比较密集。
    :param file:
    :return:
    """
    file_content = file.read()

    tmp_file_created = False
    tmp_file_path = None

    if file.name.endswith('.jpg') or file.name.endswith('.png'):
        # 图像文件处理
        nparr = np.frombuffer(file_content, np.uint8)
        data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    elif file.name.endswith('.mp4') or file.name.endswith('.avi'):
        # 视频文件处理
        with NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            tmp.write(file_content)
            tmp.flush()  # 确保所有数据写入磁盘
            tmp_file_created = True
            tmp_file_path = tmp.name
        data = cv2.VideoCapture(tmp_file_path)
    else:
        return True, {  # True 代表 Error
            "message": 'Unsupported file type'
        }

    return False, {
        'data': data,
        'tmp_file_created': tmp_file_created,
        'tmp_file_path': tmp_file_path
    }


def cal_conf(cat, cat_breed, face_breed):
    """
    结合 embedding 的 conf 和 breed 的 conf 共同计算。
    :param cat: {
            'conf':
            'cnt':
        }
    :param cat_breed: SQL 中这只猫猫的种类
    :param face_breed: FACE 中这只猫猫得到的 breed 结果。
    :return:
    """
    breed_conf = face_breed['conf'][face_breed['top5'].index(cat_breed)]
    conf = cat['conf'] / cat['cnt']
    return int(conf * breed_conf * 100)

