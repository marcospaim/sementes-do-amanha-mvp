from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class PwaTests(TestCase):
    def test_service_worker_servido_na_raiz(self):
        response = self.client.get("/sw.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn("javascript", response["Content-Type"])
        self.assertEqual(response["Service-Worker-Allowed"], "/")
        self.assertIn("sementes-v1", response.content.decode())

    def test_pagina_offline_publica(self):
        response = self.client.get(reverse("offline"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sem conexão")

    def test_manifest_referenciado(self):
        user = User.objects.create_user(username="vol", password="senha-forte-123")
        self.client.force_login(user)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "manifest.webmanifest")

    def test_pendentes_exige_login(self):
        response = self.client.get(reverse("entrega_pendentes"))
        self.assertEqual(response.status_code, 302)

    def test_pendentes_carrega_scripts(self):
        user = User.objects.create_user(username="vol", password="senha-forte-123")
        self.client.force_login(user)
        response = self.client.get(reverse("entrega_pendentes"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "offline.js")
        self.assertContains(response, "pendentes.js")
