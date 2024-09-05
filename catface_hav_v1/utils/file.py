import os
import os.path as osp

import cv2
from cv2 import VideoCapture as Video
from numpy import ndarray as Img

from ..consts import FILE_TYPE


def ensure_object_type(obj):
    """
    确保 FaceAnalysis 处理的是一个 cv2 的实体，同时判断出实体的类型。 Video / Image.
    :param obj:
    :return:
    """
    if isinstance(obj, Video):
        return obj, FILE_TYPE.video
    elif isinstance(obj, Img):
        return obj, FILE_TYPE.img
    elif os.path.exists(obj) and os.path.isfile(obj):
        file_path = obj
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        if ext in ['.jpeg', '.jpg', '.png', '.bmp', '.tiff', '.webp']:  # 图片文件
            # 使用cv2.imread()来读取图片
            image = cv2.imread(obj)
            if image is not None:
                return image, FILE_TYPE.img
            else:
                print(f"❌ Error: Couldn't open the file [{file_path}] by cv2.imread.")
        elif ext in ['.avi', '.mp4', '.mov', '.mkv', '.flv', '.wmv']:  # 视频文件
            # 使用cv2.VideoCapture()来读取视频
            video = cv2.VideoCapture(file_path)
            if video.isOpened():
                return video, FILE_TYPE.video
            else:
                print(f"❌ Error: Couldn't open the file [{file_path}] by cv2.VideoCapture.")
        else:
            print("❌ Not a supported file type.")
    else:
        print("❌ Not a cv2 object or available file path.")
    return [None] * 2


def save_frames_interval(video, **kwargs):
    """
    从 Video 对象中隔x帧保存 image
    :param video:
    :return: 返回 imgs，但实际上 list.append 函数会直接作用于原list，所以不是很必须。
    """
    if not video.isOpened():
        return []
    interval = kwargs.get('video_interval', 1)
    target_num = kwargs.get('video_num', 30)

    # FRAME-CNT and FPS
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    frame_interval = interval * fps
    if frame_count // frame_interval > target_num:
        frame_interval = frame_count // target_num // 4  # 考虑选取的一帧可能无效 cat face

    frames = []
    current_frame = 0
    while current_frame < frame_count:
        video.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = video.read()
        if not ret:
            break
        frames.append(frame)
        current_frame += frame_interval
    video.release()
    print(f"📼 INFO: Video get {len(frames)} frames.")
    return frames


def get_max_idx_next(path):
    """
    从目标文件夹中，按照 int 从小到大的方式，获取最大的序号
    :param path:
    :return: 返回开始的第一个序号。
    """
    _max_idx = 0
    for dir_name in os.listdir(path):
        if not os.path.isdir(os.path.join(path, dir_name)):
            continue
        try:
            idx = int(dir_name)
            if idx > _max_idx:
                _max_idx = idx
        except Exception as e:
            print(f"{dir_name} is not a number, pass.", e)
            continue
    return _max_idx + 1


def save_single_faces(path, faces):
    """

    :param path: 保存路径
    :param faces: Face[] 对象
    :return:
    """
    if not os.path.exists(path):
        os.mkdir(path)
    # save the faces
    for idx, face in enumerate(faces):
        cv2.imwrite(osp.join(path,  f"{idx}.jpg"), face.img)


if __name__ == "__main__":
    mp4 = cv2.VideoCapture(r"D:\DATA-CNN\CAT-MP4\ex3.mp4")
    print(ensure_object_type(mp4))
