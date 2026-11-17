from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

from estoque.models import Item

from .models import Entrega


class DuplicidadeError(Exception):
    """A família já recebeu no mesmo ciclo."""


class EstoqueInsuficienteError(Exception):
    """Saldo insuficiente para a entrega."""


def ciclo_atual():
    return timezone.localdate().strftime("%Y-%m")


@transaction.atomic
def registrar_entrega(
    *, familia, item, quantidade, usuario, ciclo=None, origem_uuid=None, sincronizado=True
):
    """Registra a saída de estoque de forma atômica, idempotente e sem duplicidade."""
    if quantidade < 1:
        raise EstoqueInsuficienteError("A quantidade deve ser maior que zero.")

    ciclo = ciclo or ciclo_atual()

    if origem_uuid is not None:
        existente = Entrega.objects.filter(origem_uuid=origem_uuid).first()
        if existente:
            return existente

    item_travado = Item.objects.select_for_update().get(pk=item.pk)

    if Entrega.objects.filter(familia=familia, ciclo=ciclo).exists():
        raise DuplicidadeError(
            "Esta família já recebeu cesta neste ciclo. O registro foi bloqueado."
        )

    if item_travado.estoque_atual < quantidade:
        raise EstoqueInsuficienteError(
            f"Saldo insuficiente de {item_travado.nome}: "
            f"disponível {item_travado.estoque_atual}, solicitado {quantidade}."
        )

    try:
        entrega = Entrega.objects.create(
            familia=familia,
            item=item_travado,
            quantidade=quantidade,
            ciclo=ciclo,
            usuario_registro=usuario,
            sincronizado_em=timezone.now() if sincronizado else None,
            **({"origem_uuid": origem_uuid} if origem_uuid else {}),
        )
    except IntegrityError as exc:
        raise DuplicidadeError(
            "Esta família já recebeu cesta neste ciclo. O registro foi bloqueado."
        ) from exc

    Item.objects.filter(pk=item_travado.pk).update(estoque_atual=F("estoque_atual") - quantidade)
    return entrega
