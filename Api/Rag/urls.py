from Api.Rag import views
from django.urls import path

urlpatterns = [
    path("bge_embedding/", views.bge_embedding, name="bge_embedding"),
]
