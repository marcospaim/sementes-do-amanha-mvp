from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from entregas.models import Entrega
from estoque.models import Item
from familias.models import Familia

User = get_user_model()

BASE_DIR = Path(__file__).resolve().parent.parent


class AcessibilidadeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vol", password="senha-forte-123")

    def test_link_para_conteudo_em_todas_as_paginas(self):
        self.client.force_login(self.user)
        for url in ("/", "/familias/nova/", "/entregas/nova/"):
            response = self.client.get(url)
            self.assertContains(response, 'class="skip"', msg_prefix=url)
            self.assertContains(response, 'href="#conteudo"', msg_prefix=url)

    def test_login_tem_rotulos_associados(self):
        response = self.client.get("/contas/login/")
        html = response.content.decode()
        self.assertIn('for="id_username"', html)
        self.assertIn('for="id_password"', html)
        self.assertIn('autocomplete="username"', html)
        self.assertIn('autocomplete="current-password"', html)

    def test_formulario_de_entrega_tem_rotulos(self):
        self.client.force_login(self.user)
        response = self.client.get("/entregas/nova/")
        html = response.content.decode()
        for campo in ("id_familia", "id_item", "id_quantidade", "id_ciclo"):
            self.assertIn(f'for="{campo}"', html)

    def test_alerta_usa_role_alert(self):
        Familia.objects.create(
            codigo="FAM-0001", responsavel_nome="Ana", endereco="Rua A", qtd_membros=2
        )
        self.client.force_login(self.user)
        response = self.client.post(
            "/familias/nova/",
            {
                "codigo": "FAM-0099",
                "responsavel_nome": "Ana",
                "endereco": "Rua A",
                "telefone": "",
                "qtd_membros": 2,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'role="alert"')

    def test_css_garante_area_de_toque_minima(self):
        css = (BASE_DIR / "static" / "css" / "app.css").read_text(encoding="utf-8")
        self.assertIn("min-height: 44px", css)
        self.assertIn("outline: 3px solid", css)

    def test_estado_nao_depende_de_cor(self):
        item = Item.objects.create(nome="Cesta básica", unidade="cesta")
        familia_pendente = Familia.objects.create(
            codigo="FAM-0001", responsavel_nome="Ana", endereco="Rua A", qtd_membros=2
        )
        familia_ok = Familia.objects.create(
            codigo="FAM-0002", responsavel_nome="Bia", endereco="Rua B", qtd_membros=3
        )
        Entrega.objects.create(
            familia=familia_pendente,
            item=item,
            quantidade=1,
            ciclo="2026-11",
            usuario_registro=self.user,
        )
        Entrega.objects.create(
            familia=familia_ok,
            item=item,
            quantidade=1,
            ciclo="2026-11",
            usuario_registro=self.user,
            sincronizado_em=timezone.now(),
        )
        self.client.force_login(self.user)
        response = self.client.get("/entregas/")
        self.assertContains(response, "Pendente")
        self.assertContains(response, "Sincronizado")
