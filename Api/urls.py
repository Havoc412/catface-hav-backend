from Api import views
from django.urls import path, include

urlpatterns = [
    path("link_test/", views.link_test, name="link_test"),
    path("search_sql/", views.search_sql, name="search"),  # 获取 SQLite 中左右数据。

    path("cnn/", include('Api.Cnn.urls')),
    # path("rag/", include('Api.Rag.urls')),
]