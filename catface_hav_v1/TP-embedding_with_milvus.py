"""
接下来。
是 Embedding 的整合。
需要实现的效果是：根据这样的文件结构，计算 Embeeding，然后打上 label 输入到 torchboard 来查看。
ROOT_DIR
├── cat_1
│   ├── 1.jpg
│   ├── 2.jpg
│   └── ...
├── cat_2
│   ├── 1.jpg
│   ├── 2.jpg
│   └── ...
└── ...
"""
import os
import cv2
import numpy as np
from torch.utils.tensorboard import SummaryWriter


from app import FaceAnalysis
from catface_hav_v1.structs import Face


from DB.face_embedding import FaceEmbeddingDB

""" CONFIG """
TAR_DIR = r"C:\Users\Havoc\PycharmProjects\YOLOv8\catface_hav_v1\test\data\faces-dif"
embedding_dim = 512


if __name__ == '__main__':
    app = FaceAnalysis(verbose=False, root="./model_zoo/models")

    #  cal all embedding
    embeddings = []
    labels = []
    # for cat_name in os.listdir(TAR_DIR):
    #     dir_path = os.path.join(TAR_DIR, cat_name)
    dir_path = TAR_DIR
    for img_name in os.listdir(dir_path):
        img_path = os.path.join(dir_path, img_name)

        # 特化使用 Face 类，直接导入 obb-pose-at 处理完后的 img。
        img = cv2.imread(img_path)
        face = Face()
        face.img = img

        app.get_embedding(face)
        embeddings.append(list(face.normed_embedding)) # 插入 Milvue 时；同时直接处理掉 norm。
        # embeddings.append(np.random.normal(0, 0.1, embedding_dim).tolist()) # 插入 Milvue 时，
        # labels.append(int(cat_name[0]))
        labels.append(int(img_name[0]))

        # # test the norm
        # print(np.dot(face.normed_embedding, face.normed_embedding))
        # exit(0)

    print(len(embeddings), len(labels))

    # # write to tensorboard
    # embeddings = np.array(embeddings)
    # writer = SummaryWriter('runs/catface-test')
    # writer.add_embedding(embeddings, metadata=labels, tag="catface")
    # writer.close()

    # # write to milvus
    faceEmbeddingDB = FaceEmbeddingDB()
    faceEmbeddingDB.insert(embeddings, labels)
