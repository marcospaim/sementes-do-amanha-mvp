from django.test import TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def test_health_retorna_ok(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_home_carrega(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Instituto Sementes do Amanhã")
