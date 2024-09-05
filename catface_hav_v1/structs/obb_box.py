from ..utils import distance, cal_degree


class BoxObb:
    def __init__(self, res):
        self.conf = res.conf[0]
        self.xy4 = res.xyxyxyxy[0]
        # attr set init
        self.eye_width = 0
        self.tpt2 = []  # top two keypoints
        self.degree = 0
        self.tpt2h = []  # hori the tpt2
        self.eye_kpts = []  # from tpt2 to kpt2
        # data cal init
        self.analyze_eyes_obb()

    def analyze_eyes_obb(self):
        self.tpt2, self.eye_width = analyze_eyes_obb2(self.xy4)
        self.degree = cal_degree(*self.tpt2)

    def predict_eye_kpts(self, tpt2h, eye_dis_ratio):
        self.tpt2h = tpt2h
        self.eye_kpts = cal_eye_kpts(self.tpt2h, self.eye_width, eye_dis_ratio)

    def rotate180(self, height, width):
        """
        配合 cv2 imread 的 shape 形式，[ height, width, channels]
        :param height:
        :param width:
        :return:
        """
        def rotate_180(x, y):
            return [width - x, height - y]
        self.eye_kpts = [rotate_180(x, y) for x, y in self.eye_kpts]


def analyze_eyes_obb2(points):
    """
    :param points:
    :return: 返回 top-two with min_len
    """
    POINTS_NUM = len(points)
    points = [[int(x), int(y)] for x, y in points]
    A = min(range(len(points)), key=lambda i: points[i][1])

    top_point = points[A]
    B_point = points[(A - 1 + POINTS_NUM) % POINTS_NUM]
    C_point = points[(A + 1) % POINTS_NUM]

    AB = distance(top_point, B_point)
    AC = distance(top_point, C_point)

    if AB > AC:
        return [top_point, B_point], AC
    else:
        return [top_point, C_point], AB


def cal_eye_kpts(points, eye_width, eye_dis_ratio=.6):
    """
    根据 obb - eye 的 top_two_points 和 宽度 来计算瞳孔关键点坐标
    :param points:
    :param eye_width:
    :param eye_dis_ratio:
    :return:
    """
    x1, y = points[0]
    x2 = points[1][0]

    if x1 > x2:  # 对于 top_two_points，存在 01 反转
        x1, x2 = x2, x1
    offset = eye_width * eye_dis_ratio
    x1 += offset
    x2 -= offset

    y += eye_width * .5
    return [[x1, y], [x2, y]]
