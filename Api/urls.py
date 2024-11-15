from Api import views
from django.urls import path, include

urlpatterns = [
    path("link_test/", views.link_test, name="link_test"),

    path("cnn/", include('Api.Cnn.urls')),
    path("rag/", include('Api.Rag.urls')),
]
