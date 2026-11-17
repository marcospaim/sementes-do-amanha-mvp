from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista, name="estoque_lista"),
    path("doacoes/nova/", views.doacao_nova, name="doacao_nova"),
]
