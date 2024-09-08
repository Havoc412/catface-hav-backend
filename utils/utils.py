from consts import BREED_CN_TO_EN, BREED_EN_TO_CN

def trans_breed(word, en_to_cn=True):
    """
    默认将 en 转换为 cn
    :param word:
    :param direction:
    :return:
    """
    return BREED_EN_TO_CN[word] if en_to_cn else BREED_CN_TO_EN[word]

