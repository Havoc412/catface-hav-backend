"""
处理 POI 等距离相关的函数计算工具文件。
"""
import math


def haversine(lat1, lon1, lat2, lon2):
    """
    计算地球上两点之间的距离.
    :param lat1: 两点的 （纬度，经度）
    :param lon1:
    :param lat2:
    :param lon2:
    :return: 单位 米(m)
    """
    # 将角度转换为弧度
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    r = 6371  # 地球平均半径，单位为公里
    return c * r * 1000  # 返回单位为米

# todo 可以包装一层函数
