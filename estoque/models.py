import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Item(models.Model):
    """Alimento ou cesta controlado em estoque."""

    class Unidade(models.TextChoices):
        QUILO = "kg", "kg"
        UNIDADE = "un", "unidade"
        CESTA = "cesta", "cesta"

    nome = models.CharField("nome", max_length=80, unique=True)
    unidade = models.CharField("unidade", max_length=10, choices=Unidade.choices)
    estoque_atual = models.PositiveIntegerField("estoque atual", default=0)
    estoque_minimo = models.PositiveIntegerField("estoque mínimo", default=0)
    ativo = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "item"
        verbose_name_plural = "itens"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.get_unidade_display()})"


class Doador(models.Model):
    class Tipo(models.TextChoices):
        PESSOA_FISICA = "pf", "Pessoa física"
        PESSOA_JURIDICA = "pj", "Pessoa jurídica"

    nome = models.CharField("nome", max_length=120)
    tipo = models.CharField("tipo", max_length=2, choices=Tipo.choices, default=Tipo.PESSOA_FISICA)
    contato = models.CharField("contato", max_length=120, blank=True)
    documento = models.CharField("documento", max_length=20, unique=True, null=True, blank=True)

    class Meta:
        verbose_name = "doador"
        verbose_name_plural = "doadores"
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.documento = (self.documento or "").strip() or None
        super().save(*args, **kwargs)


class Doacao(models.Model):
    """Entrada de itens no estoque."""

    doador = models.ForeignKey(
        Doador, verbose_name="doador", on_delete=models.SET_NULL, null=True, blank=True
    )
    item = models.ForeignKey(Item, verbose_name="item", on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField("quantidade", validators=[MinValueValidator(1)])
    data = models.DateField("data")
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="registrado por",
        on_delete=models.PROTECT,
        related_name="doacoes",
    )
    observacao = models.CharField("observação", max_length=200, blank=True)
    origem_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    criado_em = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "doação"
        verbose_name_plural = "doações"
        ordering = ["-data", "-criado_em"]

    def __str__(self):
        return f"{self.quantidade} × {self.item} em {self.data:%d/%m/%Y}"
