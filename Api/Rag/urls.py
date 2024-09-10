from Api.Rag import views
from django.urls import path

urlpatterns = [
    path("common_query/", views.common_query, name="rag_query"),
    path("detect_help/", views.detect_help, name="detect_help"),
]
