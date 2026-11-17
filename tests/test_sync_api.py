import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from entregas.models import Entrega
from estoque.models import Item
from familias.models import Familia

User = get_user_model()


class SincronizacaoEntregaTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vol", password="senha-forte-123")
        self.familia = Familia.objects.create(
            codigo="FAM-0042",
            responsavel_nome="Maria S.",
            endereco="Rua das Acácias, 120",
            qtd_membros=4,
        )
        self.item = Item.objects.create(nome="Cesta básica", unidade="cesta", estoque_atual=10)
        self.url = reverse("entrega_sync")

    def payload(self, **kwargs):
        dados = {
            "origem_uuid": str(uuid.uuid4()),
            "familia_codigo": "FAM-0042",
            "item": self.item.pk,
            "quantidade": 1,
            "ciclo": "2026-11",
        }
        dados.update(kwargs)
        return dados

    def test_exige_autenticacao(self):
        response = self.client.post(self.url, self.payload(), content_type="application/json")
        self.assertIn(response.status_code, (401, 403))
        self.assertFalse(Entrega.objects.exists())

    def test_sincroniza_entrega_valida(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.payload(), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "sincronizado")
        self.item.refresh_from_db()
        self.assertEqual(self.item.estoque_atual, 9)

    def test_reenvio_e_idempotente(self):
        self.client.force_login(self.user)
        origem = str(uuid.uuid4())
        primeira = self.client.post(
            self.url, self.payload(origem_uuid=origem), content_type="application/json"
        )
        segunda = self.client.post(
            self.url, self.payload(origem_uuid=origem), content_type="application/json"
        )
        self.assertEqual(primeira.status_code, 201)
        self.assertEqual(segunda.status_code, 200)
        self.assertEqual(Entrega.objects.count(), 1)
        self.item.refresh_from_db()
        self.assertEqual(self.item.estoque_atual, 9)

    def test_duplicidade_retorna_conflito(self):
        self.client.force_login(self.user)
        self.client.post(self.url, self.payload(), content_type="application/json")
        response = self.client.post(self.url, self.payload(), content_type="application/json")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["codigo"], "duplicidade")

    def test_estoque_insuficiente_retorna_conflito(self):
        self.item.estoque_atual = 0
        self.item.save()
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.payload(), content_type="application/json")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["codigo"], "estoque_insuficiente")

    def test_dados_invalidos_retornam_400(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url, self.payload(quantidade=0), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
