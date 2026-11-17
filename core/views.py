from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render


def health(request):
    """Verificação simples de disponibilidade usada por monitoramento e CI."""
    return JsonResponse({"status": "ok"})


@login_required
def home(request):
    """Menu inicial do MVP."""
    return render(request, "home.html")
