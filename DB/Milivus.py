import os
import json
from typing import List
from tqdm import tqdm
import numpy as np

from pymilvus import connections, Collection, db,  FieldSchema, CollectionSchema, DataType, Index, IndexType
from pymilvus import utility


class Milivus:
    def __init__(self):
        self.host = os.getenv('MILVUS_HOST', '127.0.0.1')
        self.port = os.getenv('MILVUS_PORT', '19530')
        self.db_name = os.getenv('DB_NAME', 'Catface')

        # self.collection_name = collection_name
        self.collection = None

        # FUNCTIONS
        self.connect()

    def connect(self):
        """连接到 Milvus 服务器，并启用需要的数据库"""
        connections.connect(host=self.host, port=self.port)  # ？ 这种连接不需要记录类似游标？
        db.using_database(self.db_name)
        print("Connected to Milvus.")

    def fetch_collection(self, collection_name, dim=512, description=""):
        """获取集合，没有则创建"""
        if utility.has_collection(collection_name):
            print(f"Collection {collection_name} already exists.")
            self.collection = Collection(collection_name)  # 加载现有集合
        else:
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim)
            ]
            schema = CollectionSchema(fields, description=description)
            self.collection = Collection(collection_name, schema=schema)  # 新建集合
            print(f"Collection {collection_name} created.")
            self.create_index()
        # self.load_collection()

    def create_index(self):
        index_params = {
            "index_type": IndexType.IVF_FLAT,  # 选择索引类型
            "metric_type": MetricType.L2,  # 选择距离计算方式
            "params": {"nlist": 100}  # 索引构建参数
        }
        index = Index(collection, "embedding", index_params)  # 为名为 'embedding' 的向量列创建索引
        self.collection.create_index("embedding", index)
        print("索引建立完毕。")

    def load_collection(self):
        """加载集合到内存"""
        if self.collection is not None:
            self.collection.load()
            print("Collection loaded.")
        else:
            print("Collection is not set.")

    def insert_vector(self, embeddings, cat_ids):
        """

        :param embeddings:
        :param cat_ids: cat’s id。
        :return: milvus 插入时生成的 log。
        """
        if not embeddings:
            raise ValueError("Milivus: the vectors inserted is None!")
        insert_result = self.collection.insert([embeddings, cat_ids])

        if not insert_result:
            raise Exception("Failed to insert vectors into Milvus.")
        print(f"Vectors:{len(embeddings)} inserted into Milvus.")
        return insert_result

    def search(self, query_vector, k: int = 5) -> List[int]:
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }
        results = self.collection.search(  # 直接依靠 milivus 来搜索目标
            data=[query_vector],
            anns_field="embedding",
            param=search_params,
            limit=k,
            expr=None,
            output_fields=['cat_id']
        )
        res = [(hit.entity.get('cat_id'), hit.distance) for hit in results[0]]
        return res

    def disconnect(self):
        """断开与 Milvus 的连接"""
        connections.disconnect("default")
        print("Disconnected from Milvus.")


# 使用示例
if __name__ == "__main__":
    milivus = Milvus()
