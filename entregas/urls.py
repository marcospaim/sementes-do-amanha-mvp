from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista, name="entrega_lista"),
    path("nova/", views.nova, name="entrega_nova"),
    path("<int:pk>/confirmada/", views.confirmada, name="entrega_confirmada"),
]
