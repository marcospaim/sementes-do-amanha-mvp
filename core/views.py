from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render


def health(request):
    """Verificação simples de disponibilidade usada por monitoramento e CI."""
    return JsonResponse({"status": "ok"})


@login_required
def home(request):
    """Menu inicial do MVP."""
    return render(request, "home.html")


def offline(request):
    """Página exibida pelo service worker quando não há conexão."""
    return render(request, "offline.html")


def service_worker(request):
    """Entrega o service worker na raiz para que o escopo seja todo o site."""
    conteudo = (settings.BASE_DIR / "static" / "sw.js").read_text(encoding="utf-8")
    resposta = HttpResponse(conteudo, content_type="application/javascript")
    resposta["Service-Worker-Allowed"] = "/"
    return resposta
