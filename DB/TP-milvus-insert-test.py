from pymilvus import Milvus, DataType, FieldSchema, CollectionSchema, \
    Collection, connections, db, Index, IndexType, utility
from pymilvus.client.types import MetricType

import numpy as np


""" CONFIG """
db_name = "Catface"
collection_name = "face"

if __name__ == '__main__':
    """
    创建 Face 表。
    """
    # todo BUG 创建索引失败。
    connections.connect(host='localhost', port='19530')
    db.using_database(db_name)
    print("Connect successfully!")
    dim = 512

    embeddings, cat_ids = [], []
    for _ in range(2):
        embeddings.append(np.random.normal(0, 0.1, dim).tolist())
        cat_ids.append(_)

    collection = Collection(collection_name)
    mr = collection.insert([embeddings, cat_ids])
    print(mr)
