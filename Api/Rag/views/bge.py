import json

from django.views.decorators.http import require_POST
from django.http import JsonResponse

from rag.embedding import BGE

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
    bge_model = BGE()
    embedding = bge_model.get_embedding(''.join(text))

    # ret
    return JsonResponse({'status': 200, 'message': 'Success', 'embedding': embedding.tolist()})