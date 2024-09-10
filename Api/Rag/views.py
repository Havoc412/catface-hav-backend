import json

from django.http import JsonResponse

from DB import SQLiteDB
from Api.models import catInfor

from catface_llm.LLM.LLM import GLM4Chat, Ollama3
from catface_llm.consts import LLM_CHAT_CORE_TASK
from catface_llm.VectorStore import VectorStore
from catface_llm.Embedding.PaddleEmbedding import PaddleEmbedding


embedding_model = "rocketqa-zh-base-query-encoder"


def common_query(request):
    """ 访问本地 Milvus && MongoDB 作为参考内容； ps. 也就是调用 llm.DB，之后再集成一下"""
    if request.method == 'POST':
        # get data
        data = json.loads(request.body.decode('utf-8'))
        query = data.get('query', None)
        if query is None:
            return JsonResponse({'status': 200, 'message': 'No query!'})

        # start
        collection_name = "AiTa_Popularization_Science"

        vs = VectorStore(collection_name)
        emModel = PaddleEmbedding(model=embedding_model)

        content = vs.query(query, EmbeddingModel=emModel, k=1)
        print(content)

        chat = GLM4Chat()
        res = chat.chat(query, [], content)

        print(res.content)

        return JsonResponse({'status': 200, 'answer': res.content})
    else:
        return JsonResponse({'status': 200, 'message': 'Invalid request'})


def detect_help(request):
    if request.method == 'POST':
        # get basic information
        data = json.loads(request.body.decode('utf-8'))
        query = data.get('query', None)
        cats_id = data.get('cats_id', None)
        if cats_id is None or query is None:
            return JsonResponse({'status': 200, 'message': 'No query or cats_id!'})

        # search cats's infor
        contents = []
        with SQLiteDB() as db:
            results = db.fetch_by_ids(list(cats_id))
            for result in results:
                catinfor = catInfor(result)
                contents.append(catinfor.get_infor_for_rag())

        print(contents)

        # Ask api to LLM
        chat = GLM4Chat()
        res = chat.chat(query, [], contents, task=LLM_CHAT_CORE_TASK.DETECT_CATS.value)

        print(res)

        return JsonResponse({
            "status": 200,
            "answer": res.content
        })
    else:
        return JsonResponse({'status': 200, 'message': 'Invalid request'})


