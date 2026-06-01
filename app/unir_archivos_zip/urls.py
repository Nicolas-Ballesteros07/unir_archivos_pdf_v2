from django.urls import path
from . import views

urlpatterns = [
    path('', views.subir_y_combinar, name='subir'),
    path('get-upload-url/', views.get_upload_url, name='get_upload_url'),
]