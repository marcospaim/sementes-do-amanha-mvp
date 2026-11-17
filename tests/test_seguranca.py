from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class CabecalhosDeSegurancaTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vol", password="senha-forte-123")

    def test_csp_nas_rotas_da_aplicacao(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("home"))
        csp = response["Content-Security-Policy"]
        self.assertIn("default-src 'self'", csp)
        self.assertIn("script-src 'self'", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertNotIn("script-src 'self' 'unsafe-inline'", csp)

    def test_permissoes_e_coop(self):
        response = self.client.get(reverse("offline"))
        self.assertEqual(response["Permissions-Policy"], "camera=(), microphone=(), geolocation=()")
        self.assertEqual(response["Cross-Origin-Opener-Policy"], "same-origin")

    def test_admin_fora_da_csp_estrita(self):
        response = self.client.get("/admin/login/")
        self.assertNotIn("Content-Security-Policy", response)

    def test_sessao_expira_por_inatividade(self):
        self.assertEqual(settings.SESSION_COOKIE_AGE, 8 * 60 * 60)
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)

    def test_registro_do_service_worker_em_arquivo_estatico(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "js/sw-register.js")
        self.assertNotContains(response, "navigator.serviceWorker.register")
