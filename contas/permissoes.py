from functools import wraps

from django.core.exceptions import PermissionDenied


def eh_coordenacao(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    perfil = getattr(user, "perfil", None)
    return bool(perfil and perfil.eh_coordenacao)


def coordenacao_required(view_func):
    """Permite acesso apenas à coordenação; nega por padrão."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not eh_coordenacao(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped
