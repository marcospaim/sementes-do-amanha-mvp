from django.conf import settings
from django.db import models


class PerfilUsuario(models.Model):
    class Papel(models.TextChoices):
        COORDENACAO = "coordenacao", "Coordenação"
        VOLUNTARIO = "voluntario", "Voluntário"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    papel = models.CharField(
        "papel", max_length=20, choices=Papel.choices, default=Papel.VOLUNTARIO
    )

    class Meta:
        verbose_name = "perfil de usuário"
        verbose_name_plural = "perfis de usuário"

    def __str__(self):
        return f"{self.user.get_username()} ({self.get_papel_display()})"

    @property
    def eh_coordenacao(self):
        return self.papel == self.Papel.COORDENACAO
