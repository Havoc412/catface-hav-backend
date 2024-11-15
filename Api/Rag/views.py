import os
import json

from django.views.decorators.http import require_POST
from django.http import JsonResponse

from FlagEmbedding import FlagModel

@require_POST
def bge_embedding(request):
    """
    对 BGE 词向量模型的简单封装。
    :param request:
    :return:
    """
    # STAGE 1.
    data = json.loads(request.body)
    text = data.get('text')

    # STAGE 2.
    BGE_MODEL = os.getenv("BGE_MODEL")
    model = FlagModel(BGE_MODEL,
                      query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                      use_fp16=True)  # Setting use_fp16 to True speeds up computation with a slight performance degradation

    embedding = model.encode(text)
    return JsonResponse({'status': 200, 'message': 'Success', 'embedding': embedding.tolist()})
