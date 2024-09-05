import numpy as np
import torch
import torch.backends.cudnn as cudnn

from numpy import ndarray as Img


from catface_hav_v1.utils import show_config, resize_image, preprocess_input
from catface_hav_v1.nets import Arcface


class Embedding:
    _defaults = {
        "model_path": None,
        "input_shape": [112, 112, 3],
        "backbone": "iresnet50",

        "letterbox_image": False,  # 是否使用 不失真 的 resize （what's the diff?）
        "cuda": True  # 是否使用 GPU
    }

    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)
        self.task_name = "embedding"
        for k, v in kwargs.items():
            setattr(self, k, v)
            self._defaults[k] = v

        self.load_weight()
        show_config(**self._defaults)

    def load_weight(self):
        assert self.model_path is not None, "❌ Fatal: model_path is required!"
        print("🐱 Loading weights into state dict...")
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.net = Arcface(backbone=self.backbone).eval()
        self.net.load_state_dict(torch.load(self.model_path, map_location=device), strict=False)
        print(f"{self.model_path} model loaded.")

        if self.cuda:
            self.net = self.net.cuda()
            cudnn.benchmark = True

    def get(self, face_img):
        """
        这里是加收建立在 obb-pose-at 处理之后的 Face.img 传入。
        :param face_img: 图像数据
        :return:
        """
        assert isinstance(face_img, Img), "❌ Error: face_img is not an instance of np.ndarray."
        with torch.no_grad():
            img = resize_image(face_img, [self.input_shape[1], self.input_shape[0]],
                               letterbox_image=self.letterbox_image)
            tensor = torch.from_numpy(
                np.expand_dims(np.transpose(preprocess_input(np.array(img, np.float32)), (2, 0, 1)), 0))

            if self.cuda:
                tensor = tensor.cuda()

            # predict
            embedding = self.net(tensor).cpu().numpy()[0]  # arcface 会返回一个数组。
            return embedding
