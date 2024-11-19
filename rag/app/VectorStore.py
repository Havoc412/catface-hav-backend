import os
from typing import List
from tqdm import tqdm

from elasticsearch import Elasticsearch

from ..embedding.Embeddings import BaseEmbeddings

class VectorStore:
    def __init__(self, documents, index_name="catface_docs"):
        self.index_name = index_name
        self.documents = documents

        self.dim = None
        self.vectors = None
        # 构建向量库  # UPDATE 这里还没有封装 ES。
        self.es = Elasticsearch(f"http://{os.getenv('ES_HOST')}:{os.getenv('ES_PORT')}")

    def get_vector(self, embeddingModel: BaseEmbeddings) -> List[List[float]]:
        """
        使用 Embedding 模型计算文档的嵌入向量。
        :param EmbeddingModel:
        :return:
        """
        self.vectors = []
        for doc in tqdm(self.documents, desc="Calculating embeddings"):
            self.vectors.append(embeddingModel.get_embedding(doc))
        if not self.vectors:
            raise ValueError("未获取到特征向量！")
        self.dim = len(self.vectors[0])
        return self.vectors

    def persist(self, doc_id):
        """
        持久化，存储到 ES 中
        :param doc_id: Go 记录文件时获得的文档 ID;
        :return: 上传成功失败状态
        """
        assert self.vectors is not None, "请先计算向量！"
        assert self.es.ping(), "ES 服务不可用！"

        cnt = { "success": 0, "fail": 0 }
        for vec, doc in tqdm(zip(self.vectors, self.documents), desc="Persisting vectors"):
            try:
                self.es.index(index=self.index_name, body={
                    "id": doc_id,
                    "content": doc,
                    "embedding": vec.tolist(),
                })
                cnt["success"] += 1
            except Exception as e:
                print(f"Error inserting center into Elasticsearch: {e}")
                cnt["fail"] += 1
        return cnt
