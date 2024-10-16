from consts import BREED_CN_TO_EN, BREED_EN_TO_CN
from consts.const import BREED_EN_TO_IDX


def trans_breed(word, en_to_cn=True):
    """
    默认将 en 转换为 cn
    :param word:
    :param direction:
    :return:
    """
    return BREED_EN_TO_CN[word] if en_to_cn else BREED_CN_TO_EN[word]

def trans_breedEn_to_idx(word):
    """
    将 breeds_en 转换为 breeds_idx
    :param word:
    :return:
    """
    return BREED_EN_TO_IDX.index(word) + 1