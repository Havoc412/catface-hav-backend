from django.urls import path

from Api.Rag.views import bge

urlpatterns = [
    path("bge_embedding/", bge.bge_embedding, name="bge_embedding"),
]
