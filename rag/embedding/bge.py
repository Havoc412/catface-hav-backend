import os
from FlagEmbedding import FlagModel

class BGE:
    """
    BGE 模型封装
    """
    BGE_MODEL = os.getenv("BGE_MODEL")
    def __init__(self):
        self.model = FlagModel(self.BGE_MODEL,
                              query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                              use_fp16=True)
        # Setting use_fp16 to True speeds up computation with a slight performance degradation

    def cal_embedding(self, text):
        return self.model.encode(text)
