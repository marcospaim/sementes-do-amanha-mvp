from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from contas.permissoes import coordenacao_required

from .forms import DoacaoForm
from .models import Item
from .services import registrar_doacao


@login_required
def lista(request):
    itens = Item.objects.filter(ativo=True)
    return render(request, "estoque/lista.html", {"itens": itens})


@login_required
@coordenacao_required
def doacao_nova(request):
    if request.method == "POST":
        form = DoacaoForm(request.POST)
        if form.is_valid():
            doacao = registrar_doacao(
                item=form.cleaned_data["item"],
                quantidade=form.cleaned_data["quantidade"],
                data=form.cleaned_data["data"],
                usuario=request.user,
                doador=form.cleaned_data["doador"],
                observacao=form.cleaned_data["observacao"],
            )
            messages.success(
                request,
                f"Doação registrada: {doacao.quantidade} × {doacao.item.nome}.",
            )
            return redirect("estoque_lista")
    else:
        form = DoacaoForm()
    return render(request, "estoque/doacao_form.html", {"form": form})
