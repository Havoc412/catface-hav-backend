import cv2
from ultralytics import YOLO
from math import fabs, sin, cos, radians

from catface_hav_v1.utils import distance, cal_degree
from catface_hav_v1.structs import BoxObb


class Obb:
    def __init__(self, model_file=None, verbose=False):
        assert model_file is not None
        self.model_file = model_file
        self.model = YOLO(model_file)

        self.verbose = verbose
        self.task_name = "obb"

        self.check_pt()

    def check_pt(self):
        pass

    def get(self, img, threshold=.5, eyes_distance_ratio=.6):
        # todo THINK 这里该如何方便地从 faceAnalysis 中设定参数？
        max_conf = 0
        best_res = None
        best_image = img.copy()

        # rotate for 4 times
        img_rotated = img.copy()
        for i in range(4):
            results = self.model(img_rotated, verbose=self.verbose)
            for r in results:
                obb = r.obb
                if len(obb.conf) == 0:
                    continue
                if obb.conf[0] > max_conf:
                    max_conf = obb.conf[0]
                    best_res = r
                    best_image = img_rotated.copy()
            if i < 3:
                img_rotated = cv2.rotate(img_rotated, cv2.ROTATE_90_CLOCKWISE)
        del img_rotated

        # check
        if best_res is None or max_conf < threshold:
            return [None] * 2
        best_res = best_res.cpu()
        box = BoxObb(best_res.obb)

        # rotate
        image, tpt2h = rotate(best_image, box.tpt2, box.degree)
        box.predict_eye_kpts(tpt2h, eyes_distance_ratio)
        del best_image

        return image, box  # todo image 配合上面可以作为 list 返回值。


def rotate(image, tpt2, degree):
    """

    :param image:
    :param tpt2: top two points
    :param degree:
    :return:
    """
    height, width = image.shape[:2]
    heightNew = int(width * fabs(sin(radians(degree))) + height * fabs(cos(radians(degree))))
    widthNew = int(height * fabs(sin(radians(degree))) + width * fabs(cos(radians(degree))))

    rotation_matrix = cv2.getRotationMatrix2D((width // 2, height // 2), degree, 1.0)
    rotation_matrix[0, 2] += (widthNew - width) / 2  # 增加平移的效果
    rotation_matrix[1, 2] += (heightNew - height) / 2

    rotated_image = cv2.warpAffine(image, rotation_matrix, (widthNew, heightNew))

    def rotate_point(point, M):
        """Apply rotation matrix to a point."""
        x, y = point
        new_x = M[0, 0] * x + M[0, 1] * y + M[0, 2]
        new_y = M[1, 0] * x + M[1, 1] * y + M[1, 2]
        return [new_x, new_y]

    rotated_top_two_points = [rotate_point(pt, rotation_matrix) for pt in tpt2]
    return rotated_image, rotated_top_two_points
