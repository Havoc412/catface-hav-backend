import os
from FlagEmbedding import FlagModel

from .Embeddings import BaseEmbeddings

class BGE(BaseEmbeddings):
    """
    BGE 模型封装
    """
    BGE_MODEL = os.getenv("BGE_MODEL")
    def __init__(self, path: str = '', is_api: bool = True, embedding_dim = 768) -> None:
        super().__init__(path, is_api)
        self.embedding_dim = embedding_dim
        self.model = FlagModel(self.BGE_MODEL,
                              query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                              use_fp16=True)
        # Setting use_fp16 to True speeds up computation with a slight performance degradation

    def get_embedding(self, text):
        return self.model.encode(text)
