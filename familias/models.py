from django.core.validators import MinValueValidator
from django.db import models


class Familia(models.Model):
    """Unidade beneficiária cadastrada uma única vez."""

    codigo = models.CharField("código", max_length=12, unique=True)
    responsavel_nome = models.CharField("nome do responsável", max_length=120)
    endereco = models.CharField("endereço", max_length=200)
    telefone = models.CharField("telefone", max_length=20, blank=True)
    qtd_membros = models.PositiveSmallIntegerField(
        "quantidade de membros", validators=[MinValueValidator(1)]
    )
    ativo = models.BooleanField("ativo", default=True)
    criado_em = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "família"
        verbose_name_plural = "famílias"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} — {self.responsavel_nome}"

    def save(self, *args, **kwargs):
        self.codigo = (self.codigo or "").strip().upper()
        self.responsavel_nome = (self.responsavel_nome or "").strip()
        self.endereco = (self.endereco or "").strip()
        super().save(*args, **kwargs)
