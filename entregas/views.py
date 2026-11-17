from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EntregaForm
from .models import Entrega
from .services import DuplicidadeError, EstoqueInsuficienteError, registrar_entrega


@login_required
def nova(request):
    familia_inicial = request.GET.get("familia")
    dados_iniciais = {"familia": familia_inicial} if familia_inicial else None

    if request.method == "POST":
        form = EntregaForm(request.POST)
        if form.is_valid():
            try:
                entrega = registrar_entrega(
                    familia=form.cleaned_data["familia"],
                    item=form.cleaned_data["item"],
                    quantidade=form.cleaned_data["quantidade"],
                    ciclo=form.cleaned_data["ciclo"],
                    usuario=request.user,
                )
            except DuplicidadeError as exc:
                form.add_error(None, str(exc))
            except EstoqueInsuficienteError as exc:
                form.add_error(None, str(exc))
            else:
                return redirect("entrega_confirmada", pk=entrega.pk)
    else:
        form = EntregaForm(initial=dados_iniciais)

    return render(request, "entregas/form.html", {"form": form})


@login_required
def confirmada(request, pk):
    entrega = get_object_or_404(Entrega.objects.select_related("familia", "item"), pk=pk)
    return render(request, "entregas/confirmada.html", {"entrega": entrega})


@login_required
def lista(request):
    entregas = Entrega.objects.select_related("familia", "item").all()[:100]
    return render(request, "entregas/lista.html", {"entregas": entregas})
