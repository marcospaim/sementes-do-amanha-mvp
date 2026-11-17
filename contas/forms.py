from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.core.exceptions import ValidationError

MAX_TENTATIVAS = 5
JANELA_SEGUNDOS = 15 * 60


def _chave(request, username):
    ip = request.META.get("REMOTE_ADDR", "desconhecido")
    return f"login:tentativas:{ip}:{(username or '').lower()}"


class LoginComBloqueioForm(AuthenticationForm):
    """Autenticação com bloqueio temporário após tentativas inválidas."""

    error_messages = {
        "invalid_login": "Usuário ou senha inválidos.",
        "inactive": "Usuário ou senha inválidos.",
    }

    def clean(self):
        chave = _chave(self.request, self.cleaned_data.get("username"))
        tentativas = cache.get(chave, 0)
        if tentativas >= MAX_TENTATIVAS:
            raise ValidationError(
                "Muitas tentativas inválidas. Tente novamente em alguns minutos.",
                code="bloqueado",
            )
        try:
            resultado = super().clean()
        except ValidationError:
            cache.set(chave, tentativas + 1, JANELA_SEGUNDOS)
            raise
        cache.delete(chave)
        return resultado


class FormularioLogin(LoginComBloqueioForm):
    username = forms.CharField(
        label="E-mail ou usuário",
        widget=forms.TextInput(attrs={"autocomplete": "username", "autofocus": True}),
    )
    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
