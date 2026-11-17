"""Rotas raiz do projeto."""

from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from contas.views import LoginComBloqueioView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("contas/login/", LoginComBloqueioView.as_view(), name="login"),
    path("contas/logout/", LogoutView.as_view(), name="logout"),
    path("", include("core.urls")),
]
