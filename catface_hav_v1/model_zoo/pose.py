import cv2
import torch
from ultralytics import YOLO

# 关键点 BGR 配色
kpt_radius = 3
kpt_color_map = {
    0: {'name': 'Left Eye', 'color': [255, 0, 0], 'radius': kpt_radius},  # eye - l
    1: {'name': 'Right Eye', 'color': [150, 150, 0], 'radius': kpt_radius},  # eye - r
    2: {'name': 'Nose', 'color': [0, 0, 255], 'radius': kpt_radius},  # nose

    3: {'name': 'Left Ear - 1', 'color': [0, 255, 0], 'radius': kpt_radius},  # ear - l - 1
    4: {'name': 'Left Ear - 3', 'color': [0, 255, 0], 'radius': kpt_radius},  # ear - l - 3

    5: {'name': 'Right Ear - 1', 'color': [193, 182, 255], 'radius': kpt_radius},  # ear - r - 1
    6: {'name': 'Right Ear - 2', 'color': [193, 182, 255], 'radius': kpt_radius},  # ear - r - 3
}
# 现阶段比较常用的就是 5kpt 和 7kpt，7kpt 普遍效果更好一些。


class Pose:
    def __init__(self, model_file=None, verbose=False):
        assert model_file is not None
        self.model_file = model_file
        self.model = YOLO(model_file)

        self.verbose = verbose
        self.task_name = "pose"
        self.kpt_num = 0
        self.check_pt()

    def check_pt(self):
        """ CHECK it's a real pose pt """
        self.kpt_num = self.get_kpts_num()
        assert self.kpt_num in [3, 5, 7], f"kpt_num is only for 3, 5,7, but now is [{self.kpt_num}]"

    def get_kpts_num(self):
        """
        用一个随机数据测试模型的输出
        :return:
        """
        dummy_input = torch.rand(1, 3, 640, 640)  # 根据需要调整输入大小
        outputs = self.model(dummy_input, verbose=False)[0]
        # check
        if outputs is None:
            return None
        if not hasattr(outputs, 'keypoints') or outputs.keypoints is None:
            return None
        if not hasattr(outputs.keypoints, 'shape') or len(outputs.keypoints.shape) != 3:
            return None

        # 分析输出，确定关键点数量
        keypoint_count = outputs.keypoints.shape[2] // 3  # 假设每个关键点有3个值 (x, y, confidence)
        return keypoint_count

    def get(self, img, box_obb=None, threshold=.5):
        best_result = self.model(img, verbose=self.verbose)[0]
        best_image = img.copy()
        img_temp = img.copy()
        # obb 有效，那么尝试 旋转180° 识别。
        if box_obb is not None:
            img_temp = cv2.rotate(img_temp, cv2.ROTATE_180)
            result = self.model(img_temp, verbose=self.verbose)[0]
            # print(best_result.boxes.conf, result.boxes.conf)
            if len(result.boxes.conf) > 0 and \
                    (len(best_result.boxes.conf) == 0 or result.boxes.conf[0] > best_result.boxes.conf[0]):
                best_result = result
                box_obb.rotate180(*img_temp.shape[:2])
                best_image = img_temp
        del img_temp
        # check
        if len(best_result.boxes.conf) == 0 or best_result.boxes.conf[0] < threshold:
            return [None] * 2
        best_result = best_result.cpu()
        return best_image, best_result


if __name__ == "__main__":
    model = Pose("./models/group-1/obb.pt")
    print(model.get_kpts_num())
