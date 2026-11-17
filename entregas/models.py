import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from estoque.models import Item
from familias.models import Familia


class Entrega(models.Model):
    """Saída de item para uma família, inclusive registrada offline."""

    familia = models.ForeignKey(
        Familia, verbose_name="família", on_delete=models.PROTECT, related_name="entregas"
    )
    item = models.ForeignKey(
        Item, verbose_name="item", on_delete=models.PROTECT, related_name="entregas"
    )
    quantidade = models.PositiveIntegerField("quantidade", validators=[MinValueValidator(1)])
    ciclo = models.CharField("ciclo", max_length=7)
    data = models.DateTimeField("data", auto_now_add=True)
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="registrado por",
        on_delete=models.PROTECT,
        related_name="entregas",
    )
    origem_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    sincronizado_em = models.DateTimeField("sincronizado em", null=True, blank=True)

    class Meta:
        verbose_name = "entrega"
        verbose_name_plural = "entregas"
        ordering = ["-data"]
        constraints = [
            models.UniqueConstraint(
                fields=["familia", "ciclo"], name="entrega_unica_por_familia_ciclo"
            ),
            models.CheckConstraint(
                condition=models.Q(quantidade__gte=1), name="entrega_quantidade_positiva"
            ),
        ]

    def __str__(self):
        return f"{self.familia.codigo} — {self.item.nome} — {self.ciclo}"
