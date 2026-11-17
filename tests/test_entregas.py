import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from entregas.models import Entrega
from entregas.services import (
    DuplicidadeError,
    EstoqueInsuficienteError,
    registrar_entrega,
)
from estoque.models import Item
from familias.models import Familia

User = get_user_model()


class EntregaServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vol", password="senha-forte-123")
        self.familia = Familia.objects.create(
            codigo="FAM-0042",
            responsavel_nome="Maria S.",
            endereco="Rua das Acácias, 120",
            qtd_membros=4,
        )
        self.item = Item.objects.create(nome="Cesta básica", unidade="cesta", estoque_atual=10)

    def test_entrega_reduz_estoque(self):
        registrar_entrega(
            familia=self.familia,
            item=self.item,
            quantidade=2,
            usuario=self.user,
            ciclo="2026-11",
        )
        self.item.refresh_from_db()
        self.assertEqual(self.item.estoque_atual, 8)

    def test_bloqueia_duplicidade_no_mesmo_ciclo(self):
        registrar_entrega(
            familia=self.familia, item=self.item, quantidade=1, usuario=self.user, ciclo="2026-11"
        )
        with self.assertRaises(DuplicidadeError):
            registrar_entrega(
                familia=self.familia,
                item=self.item,
                quantidade=1,
                usuario=self.user,
                ciclo="2026-11",
            )
        self.assertEqual(Entrega.objects.count(), 1)

    def test_permite_mesma_familia_em_outro_ciclo(self):
        registrar_entrega(
            familia=self.familia, item=self.item, quantidade=1, usuario=self.user, ciclo="2026-11"
        )
        registrar_entrega(
            familia=self.familia, item=self.item, quantidade=1, usuario=self.user, ciclo="2026-12"
        )
        self.assertEqual(Entrega.objects.count(), 2)

    def test_bloqueia_estoque_insuficiente(self):
        self.item.estoque_atual = 1
        self.item.save()
        with self.assertRaises(EstoqueInsuficienteError):
            registrar_entrega(
                familia=self.familia,
                item=self.item,
                quantidade=5,
                usuario=self.user,
                ciclo="2026-11",
            )
        self.item.refresh_from_db()
        self.assertEqual(self.item.estoque_atual, 1)
        self.assertFalse(Entrega.objects.exists())

    def test_idempotente_por_origem_uuid(self):
        origem = uuid.uuid4()
        primeira = registrar_entrega(
            familia=self.familia,
            item=self.item,
            quantidade=1,
            usuario=self.user,
            ciclo="2026-11",
            origem_uuid=origem,
        )
        segunda = registrar_entrega(
            familia=self.familia,
            item=self.item,
            quantidade=1,
            usuario=self.user,
            ciclo="2026-11",
            origem_uuid=origem,
        )
        self.assertEqual(primeira.pk, segunda.pk)
        self.assertEqual(Entrega.objects.count(), 1)


class EntregaViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vol", password="senha-forte-123")
        self.familia = Familia.objects.create(
            codigo="FAM-0042",
            responsavel_nome="Maria S.",
            endereco="Rua das Acácias, 120",
            qtd_membros=4,
        )
        self.item = Item.objects.create(nome="Cesta básica", unidade="cesta", estoque_atual=10)

    def test_exige_login(self):
        response = self.client.get(reverse("entrega_nova"))
        self.assertEqual(response.status_code, 302)

    def test_voluntario_registra_entrega(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("entrega_nova"),
            {
                "familia": self.familia.pk,
                "item": self.item.pk,
                "quantidade": 1,
                "ciclo": "2026-11",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Entrega.objects.filter(familia=self.familia, ciclo="2026-11").exists())
        self.item.refresh_from_db()
        self.assertEqual(self.item.estoque_atual, 9)

    def test_duplicidade_mostra_mensagem(self):
        registrar_entrega(
            familia=self.familia, item=self.item, quantidade=1, usuario=self.user, ciclo="2026-11"
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("entrega_nova"),
            {
                "familia": self.familia.pk,
                "item": self.item.pk,
                "quantidade": 1,
                "ciclo": "2026-11",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "já recebeu cesta neste ciclo")
