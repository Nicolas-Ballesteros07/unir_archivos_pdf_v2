from django.urls import path
from . import views

urlpatterns = [
    path('', views.subir_y_combinar, name='subir'),
]