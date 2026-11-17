from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from contas.models import PerfilUsuario
from contas.permissoes import eh_coordenacao

User = get_user_model()


class PerfilTests(TestCase):
    def test_perfil_criado_automaticamente_como_voluntario(self):
        user = User.objects.create_user(username="vol", password="senha-forte-123")
        self.assertTrue(hasattr(user, "perfil"))
        self.assertEqual(user.perfil.papel, PerfilUsuario.Papel.VOLUNTARIO)

    def test_coordenacao_reconhecida(self):
        user = User.objects.create_user(username="coord", password="senha-forte-123")
        user.perfil.papel = PerfilUsuario.Papel.COORDENACAO
        user.perfil.save()
        self.assertTrue(eh_coordenacao(user))

    def test_superusuario_e_coordenacao(self):
        user = User.objects.create_superuser(
            username="admin", email="admin@example.org", password="senha-forte-123"
        )
        self.assertTrue(eh_coordenacao(user))

    def test_anonimo_nao_e_coordenacao(self):
        from django.contrib.auth.models import AnonymousUser

        self.assertFalse(eh_coordenacao(AnonymousUser()))


class AutenticacaoTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username="vol", password="senha-forte-123")

    def test_home_exige_login(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")

    def test_login_valido_autentica(self):
        response = self.client.post(
            reverse("login"), {"username": "vol", "password": "senha-forte-123"}
        )
        self.assertRedirects(response, reverse("home"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_invalido_mostra_mensagem_generica(self):
        response = self.client.post(reverse("login"), {"username": "vol", "password": "errada"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuário ou senha inválidos.")
        self.assertNotContains(response, "senha-forte")

    def test_bloqueio_apos_cinco_tentativas(self):
        for _ in range(5):
            self.client.post(reverse("login"), {"username": "vol", "password": "errada"})
        response = self.client.post(
            reverse("login"), {"username": "vol", "password": "senha-forte-123"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Muitas tentativas inválidas")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_invalida_sessao(self):
        self.client.login(username="vol", password="senha-forte-123")
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)
