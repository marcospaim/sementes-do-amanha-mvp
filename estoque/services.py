from django.db import transaction
from django.db.models import F

from .models import Doacao, Item


class EstoqueError(Exception):
    """Erro de regra de negócio do estoque."""


@transaction.atomic
def registrar_doacao(
    *, item, quantidade, data, usuario, doador=None, observacao="", origem_uuid=None
):
    """Registra entrada de estoque de forma atômica e idempotente."""
    if quantidade < 1:
        raise EstoqueError("A quantidade deve ser maior que zero.")

    if origem_uuid is not None:
        existente = Doacao.objects.filter(origem_uuid=origem_uuid).first()
        if existente:
            return existente

    item_travado = Item.objects.select_for_update().get(pk=item.pk)
    doacao = Doacao.objects.create(
        item=item_travado,
        quantidade=quantidade,
        data=data,
        usuario_registro=usuario,
        doador=doador,
        observacao=observacao,
        **({"origem_uuid": origem_uuid} if origem_uuid else {}),
    )
    Item.objects.filter(pk=item_travado.pk).update(estoque_atual=F("estoque_atual") + quantidade)
    return doacao
