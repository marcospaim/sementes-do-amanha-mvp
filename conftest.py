import pytest
from django.test import override_settings


@pytest.fixture(autouse=True)
def ambiente_de_teste():
    """Mantém os testes independentes do endurecimento de produção (HTTPS/HSTS)."""
    with override_settings(
        SECURE_SSL_REDIRECT=False,
        SECURE_HSTS_SECONDS=0,
        SESSION_COOKIE_SECURE=False,
        CSRF_COOKIE_SECURE=False,
        ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"],
    ):
        yield
