from django.urls import path

from . import views
from .painel import painel, relatorio_csv, relatorio_pdf

urlpatterns = [
    path("", views.home, name="home"),
    path("health/", views.health, name="health"),
    path("offline/", views.offline, name="offline"),
    path("sw.js", views.service_worker, name="service_worker"),
    path("painel/", painel, name="painel"),
    path("painel/relatorio.pdf", relatorio_pdf, name="relatorio_pdf"),
    path("painel/relatorio.csv", relatorio_csv, name="relatorio_csv"),
]
