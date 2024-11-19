import json

from django.views.decorators.http import require_POST
from django.http import JsonResponse

from rag.utils.file import ReadFiles
from rag.embedding.bge import BGE
from rag.app.VectorStore import VectorStore

@require_POST
def upload_doc_titleChunk(request):
    # STAGE 1.
    data = json.loads(request.body)
    file_id = data.get('file_id')
    file_path = data.get('file_path')

    title = data.get('title')  # INFO 分块依据。

    # STAGE 2.1
    reader = ReadFiles(file_path)
    docs = reader.get_chunk_by_title(title)

    # STAGE 2.2
    bge_model = BGE()
    vector_store = VectorStore(docs)

    vector_store.get_vector(bge_model)
    status = vector_store.persist(file_id)

    return JsonResponse({'status': 200, 'message': 'Success', "status": status})







