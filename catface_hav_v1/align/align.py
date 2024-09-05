import cv2
import numpy as np
from skimage import transform as trans


class AT:
    def __init__(self):
        self._dst_kpts = np.array([
            [72, 120],
            [180, 119],
            [129, 185]
        ], dtype=np.float32)

    def estimate_norm(self, skpts, image_size=256):
        assert image_size % 256 == 0
        # if image_size % 256 == 0:  # todo 目前只考虑 112px 这一种
        ratio = float(image_size)/256.0
        dst = self._dst_kpts * ratio
        tform = trans.SimilarityTransform()  # 和 getAffineTransform 应该是类似的效果，但是 getAffineTransform 只作用于三个点
        tform.estimate(skpts, dst)
        M = tform.params[0:2, :]  # 实际也只有矩阵的前两行有用
        return M

    def norm_crop(self, img, skpts, image_size=256):
        M = self.estimate_norm(skpts, image_size)
        warped = cv2.warpAffine(img, M, (image_size, image_size))
        return warped

    def get(self, img, face, image_size=256):
        aimg = self.norm_crop(img, face.kpts[:3], image_size)  # 目前选取前三个点位
        face.img = aimg
        return face.img


if __name__ == "__main__":
    test_skpt = np.array([
        [12, 0], [10, 12], [0, 0]
    ])
    at = AT()
    # at.get(None, test_skpt)

