from django.urls import path

from . import views

urlpatterns = [
    path("", views.upload, name="upload"),
    path("history/", views.history, name="history"),
    path("scan/<int:pk>/", views.detail, name="detail"),
    path("scan/<int:pk>/download/", views.download_text, name="download"),
    path("scan/<int:pk>/delete/", views.delete, name="delete"),
]
