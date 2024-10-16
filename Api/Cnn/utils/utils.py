
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
    breed_conf = face_breed['conf'][face_breed['top5'].index(cat_breed)]
    conf = cat['conf'] / cat['cnt']
    return int(conf * breed_conf * 100)

