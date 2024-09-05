"""

"""

import os
import cv2

from app import FaceAnalysis
from catface_hav_v1.consts import FACE_MODE
from catface_hav_v1.utils import save_single_faces

if __name__ == '__main__':
    app = FaceAnalysis(verbose=False)

    img = cv2.imread(r"D:\DATA-CNN\DATA-catface-obb-threepts\images\train\1.jpg")
    faces = app.get(img, mode=FACE_MODE.single)

    for face in faces:
        print(face.embedding)


