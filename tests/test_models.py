import uuid

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from entregas.models import Entrega
from estoque.models import Doacao, Doador, Item
from familias.models import Familia

User = get_user_model()


class FamiliaModelTests(TestCase):
    def test_codigo_e_normalizado(self):
        familia = Familia.objects.create(
            codigo=" fam-0001 ",
            responsavel_nome="Maria S.",
            endereco="Rua das Acácias, 120",
            qtd_membros=4,
        )
        self.assertEqual(familia.codigo, "FAM-0001")

    def test_codigo_unico(self):
        Familia.objects.create(
            codigo="FAM-0001",
            responsavel_nome="Maria S.",
            endereco="Rua das Acácias, 120",
            qtd_membros=4,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Familia.objects.create(
                codigo="FAM-0001",
                responsavel_nome="Outra",
                endereco="Rua B",
                qtd_membros=2,
            )


class EstoqueModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vol", password="senha-forte-123")

    def test_documento_vazio_vira_nulo(self):
        doador = Doador.objects.create(nome="Mercado Central", documento="")
        self.assertIsNone(doador.documento)

    def test_doacao_gera_uuid_unico(self):
        item = Item.objects.create(nome="Cesta básica", unidade="cesta")
        doacao = Doacao.objects.create(
            item=item, quantidade=10, data="2026-11-01", usuario_registro=self.user
        )
        self.assertIsInstance(doacao.origem_uuid, uuid.UUID)


class EntregaModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vol", password="senha-forte-123")
        self.familia = Familia.objects.create(
            codigo="FAM-0042",
            responsavel_nome="Maria S.",
            endereco="Rua das Acácias, 120",
            qtd_membros=4,
        )
        self.item = Item.objects.create(nome="Cesta básica", unidade="cesta")

    def test_uma_entrega_por_familia_por_ciclo(self):
        Entrega.objects.create(
            familia=self.familia,
            item=self.item,
            quantidade=1,
            ciclo="2026-11",
            usuario_registro=self.user,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Entrega.objects.create(
                familia=self.familia,
                item=self.item,
                quantidade=1,
                ciclo="2026-11",
                usuario_registro=self.user,
            )

    def test_mesmo_ciclo_permite_outra_familia(self):
        outra = Familia.objects.create(
            codigo="FAM-0043",
            responsavel_nome="João P.",
            endereco="Rua B, 10",
            qtd_membros=2,
        )
        for familia in (self.familia, outra):
            Entrega.objects.create(
                familia=familia,
                item=self.item,
                quantidade=1,
                ciclo="2026-11",
                usuario_registro=self.user,
            )
        self.assertEqual(Entrega.objects.count(), 2)
