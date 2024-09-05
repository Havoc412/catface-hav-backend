"""
整合 图像处理 相关的函数。
"""

import cv2
import numpy as np


def resize_image(image, size, letterbox_image):
    """
    调整图像大小。

    参数：
    - image: 输入图像，类型为 OpenCV 图像 (即 numpy 数组)。
    - size: 目标尺寸 (宽, 高)。
    - letterbox_image: 布尔值，是否使用 letterbox 图像（保持长宽比并填充灰色边框）。

    返回：
    - new_image: 调整大小后的图像。
    """
    ih, iw = image.shape[:2]  # 获取输入图像的宽和高
    w, h = size  # 目标尺寸的宽和高

    if letterbox_image:
        # 计算缩放比例以保持长宽比
        scale = min(w / iw, h / ih)
        nw = int(iw * scale)
        nh = int(ih * scale)

        # 使用缩放比例调整图像大小
        image_resized = cv2.resize(image, (nw, nh), interpolation=cv2.INTER_CUBIC)

        # 创建一个新的灰色背景图像
        new_image = np.full((h, w, 3), 128, dtype=np.uint8)

        # 将调整大小后的图像粘贴到灰色背景图像的中央
        top = (h - nh) // 2
        left = (w - nw) // 2
        new_image[top:top+nh, left:left+nw, :] = image_resized
    else:
        # 直接调整图像大小到目标尺寸，不保持长宽比
        new_image = cv2.resize(image, (w, h), interpolation=cv2.INTER_CUBIC)

    return new_image


def preprocess_input(image):
    """ 数据预处理 """
    image /= 255.0
    image -= 0.5
    image /= 0.5
    return image

# image = cv2.imread('path_to_your_image.jpg')
# resized_image = resize_image(image, (300, 300), letterbox_image=True)
# cv2.imwrite('resized_image.jpg', resized_image)
