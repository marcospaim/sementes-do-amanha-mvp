from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista, name="familia_lista"),
    path("nova/", views.criar, name="familia_nova"),
    path("<int:pk>/", views.detalhe, name="familia_detalhe"),
]
