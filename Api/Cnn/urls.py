from Api.Cnn import views
from django.urls import path

urlpatterns = [
    path("cnn_test/", views.cnn_test, name="cnn_test"),

    path("detect_cat/", views.detect_cat, name="detect_cat"),
    # path("add_cat/", views.add_cat, name="add_cat"),  # TODO 迁移到 Go
]