import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from contas.models import PerfilUsuario
from estoque.forms import DoacaoForm
from estoque.models import Doacao, Item
from estoque.services import EstoqueError, registrar_doacao

User = get_user_model()


class DoacaoServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="coord", password="senha-forte-123")
        self.item = Item.objects.create(nome="Cesta básica", unidade="cesta", estoque_atual=5)

    def test_doacao_soma_ao_estoque(self):
        registrar_doacao(item=self.item, quantidade=10, data="2026-11-16", usuario=self.user)
        self.item.refresh_from_db()
        self.assertEqual(self.item.estoque_atual, 15)

    def test_doacao_idempotente_por_origem_uuid(self):
        origem = uuid.uuid4()
        primeira = registrar_doacao(
            item=self.item, quantidade=10, data="2026-11-16", usuario=self.user, origem_uuid=origem
        )
        segunda = registrar_doacao(
            item=self.item, quantidade=10, data="2026-11-16", usuario=self.user, origem_uuid=origem
        )
        self.item.refresh_from_db()
        self.assertEqual(primeira.pk, segunda.pk)
        self.assertEqual(self.item.estoque_atual, 15)
        self.assertEqual(Doacao.objects.count(), 1)

    def test_quantidade_invalida(self):
        with self.assertRaises(EstoqueError):
            registrar_doacao(item=self.item, quantidade=0, data="2026-11-16", usuario=self.user)


class DoacaoViewTests(TestCase):
    def setUp(self):
        self.item = Item.objects.create(nome="Cesta básica", unidade="cesta")
        self.user = User.objects.create_user(username="vol", password="senha-forte-123")

    def test_voluntario_nao_registra_doacao(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("doacao_nova"))
        self.assertEqual(response.status_code, 403)

    def test_coordenacao_registra_doacao(self):
        self.user.perfil.papel = PerfilUsuario.Papel.COORDENACAO
        self.user.perfil.save()
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("doacao_nova"),
            {"item": self.item.pk, "quantidade": 8, "data": "2026-11-16", "observacao": ""},
        )
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertEqual(self.item.estoque_atual, 8)

    def test_form_recusa_quantidade_zero(self):
        form = DoacaoForm(data={"item": self.item.pk, "quantidade": 0, "data": "2026-11-16"})
        self.assertFalse(form.is_valid())
