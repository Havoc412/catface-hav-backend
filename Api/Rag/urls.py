from django.urls import path

from Api.Rag.views import bge
from Api.Rag.views import doc

urlpatterns = [
    path("bge_embedding", bge.bge_embedding, name="bge_embedding"),

    path("doc_title", doc.upload_doc_titleChunk, name="doc_title")
]
