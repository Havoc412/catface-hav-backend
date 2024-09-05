import os.path as osp

from .obb import Obb
from .pose import Pose
from .embedding import Embedding


class ModelRouter:
    def __init__(self, pt_file):
        self.pt_file = pt_file

    def get_model(self, **kwargs):
        #  todo 先这样粗糙的做区分。 insightFace 的实现方式好像是根据模型的 input 等数据来作为标准。
        if self.pt_file.endswith("embedding.pt") or self.pt_file.endswith("embedding.pth"):
            return Embedding(model_path=self.pt_file)
        elif self.pt_file.endswith("obb.pt") or self.pt_file.endswith("obb.pth"):
            verbose = kwargs.get("verbose", False)
            return Obb(self.pt_file, verbose)
        elif self.pt_file.endswith("pose.pt") or self.pt_file.endswith("pose.pth"):
            verbose = kwargs.get("verbose", False)
            return Pose(self.pt_file, verbose)
        else:
            print(f"⚠️ Could not support model [{self.pt_file}], only for obb, pose, embedding.")
            return None


def get_model(path, **kwargs):
    assert path.endswith('.pt') or path.endswith('.pth'), f"[{path}] is not a pt file."
    assert osp.exists(path), f"[{path}] is not exists."
    assert osp.isfile(path), f"[{path}] is not a file, please check."
    router = ModelRouter(path)
    model = router.get_model(**kwargs)
    return model
