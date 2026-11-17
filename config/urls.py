"""Rotas raiz do projeto."""

from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from contas.views import LoginComBloqueioView
from entregas.api import SincronizarEntregaView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("contas/login/", LoginComBloqueioView.as_view(), name="login"),
    path("contas/logout/", LogoutView.as_view(), name="logout"),
    path("api/entregas/sincronizar/", SincronizarEntregaView.as_view(), name="entrega_sync"),
    path("familias/", include("familias.urls")),
    path("estoque/", include("estoque.urls")),
    path("entregas/", include("entregas.urls")),
    path("", include("core.urls")),
]
