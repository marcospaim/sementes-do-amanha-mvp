from django.http import JsonResponse
from django.shortcuts import render


def health(request):
    """Verificação simples de disponibilidade usada por monitoramento e CI."""
    return JsonResponse({"status": "ok"})


def home(request):
    """Página inicial provisória; será substituída pelo menu do MVP."""
    return render(request, "home.html")
