from enum import Enum


class FILE_TYPE(Enum):
    img = 0
    video = 1


class FACE_MODE(Enum):
    single = 0
    multi = 1

    @staticmethod  # 或者可以用 @classmethod 来实现。
    def check(mode):
        return mode in FACE_MODE
