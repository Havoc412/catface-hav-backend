import numpy as np
from numpy.linalg import norm as l2norm


class Face:
    def __init__(self, box=None, conf=None, kpts=None):
        self.box = box
        self.conf = conf
        self.kpts = kpts.numpy()[:, :2] if kpts is not None else None

        # self.img  # by detect

    def change_eye_kpts(self, eye_kpts):
        kpts = np.array(eye_kpts)
        # handle rotate 180°
        if kpts[0, 0] > kpts[1, 0]:
            kpts[[0, 1]] = kpts[[1, 0]]  # tip 简洁写法
        self.kpts[:2] = kpts

    def __getattr__(self, name):
        return None

    @property
    def embedding_norm(self):
        if self.embedding is None:
            return None
        return l2norm(self.embedding)

    @property
    def normed_embedding(self):
        if self.embedding is None:
            return None
        return self.embedding / self.embedding_norm
