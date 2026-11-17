from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from contas.permissoes import eh_coordenacao

from .forms import FamiliaForm
from .models import Familia


@login_required
def lista(request):
    termo = (request.GET.get("q") or "").strip()
    familias = Familia.objects.all()
    if termo:
        familias = familias.filter(
            Q(codigo__icontains=termo) | Q(responsavel_nome__icontains=termo)
        )
    return render(
        request,
        "familias/lista.html",
        {
            "familias": familias,
            "termo": termo,
            "pode_ver_contato": eh_coordenacao(request.user),
        },
    )


@login_required
def detalhe(request, pk):
    familia = get_object_or_404(Familia, pk=pk)
    return render(
        request,
        "familias/detalhe.html",
        {"familia": familia, "pode_ver_contato": eh_coordenacao(request.user)},
    )


@login_required
def criar(request):
    if request.method == "POST":
        form = FamiliaForm(request.POST)
        if form.is_valid():
            familia = form.save()
            messages.success(request, f"Família {familia.codigo} cadastrada com sucesso.")
            return redirect("familia_detalhe", pk=familia.pk)
    else:
        form = FamiliaForm()
    return render(request, "familias/form.html", {"form": form})
