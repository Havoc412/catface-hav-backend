import math


def distance(pt1, pt2):
    res = math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)
    return res


def cal_degree(pt1, pt2):
    """ 计算偏移角度 """
    tan_value = (pt1[1] - pt2[1]) / (pt1[0] - pt2[0] + 1e-10)  # tip 增加一个浮点数，防止溢出

    radians = math.atan(tan_value)
    degrees = math.degrees(radians)

    return degrees
