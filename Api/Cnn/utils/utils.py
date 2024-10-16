from utils import trans_breedEn_to_idx

def test():
    return "Cnn test."

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
    base_conf = cat['conf'] / cat['cnt']

    breed_conf = 0
    for breed, conf in zip(face_breed['top5'], face_breed['conf']):
        print(breed, conf, trans_breedEn_to_idx(breed))
        breed_conf += cat_breed.get(trans_breedEn_to_idx(breed), 0) * conf

    print("🚩", base_conf, breed_conf)

    return int(base_conf * breed_conf * 100)

