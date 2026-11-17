from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from contas.models import PerfilUsuario
from entregas.services import registrar_entrega
from estoque.models import Item
from familias.models import Familia

User = get_user_model()


class PainelTests(TestCase):
    def setUp(self):
        self.familia = Familia.objects.create(
            codigo="FAM-0042",
            responsavel_nome="Maria S.",
            endereco="Rua das Acácias, 120",
            qtd_membros=4,
        )
        self.item = Item.objects.create(nome="Cesta básica", unidade="cesta", estoque_atual=10)
        self.coord = User.objects.create_user(username="coord", password="senha-forte-123")
        self.coord.perfil.papel = PerfilUsuario.Papel.COORDENACAO
        self.coord.perfil.save()
        self.vol = User.objects.create_user(username="vol", password="senha-forte-123")
        registrar_entrega(
            familia=self.familia,
            item=self.item,
            quantidade=2,
            usuario=self.coord,
            ciclo="2026-11",
        )

    def test_voluntario_recebe_403(self):
        self.client.force_login(self.vol)
        for nome in ("painel", "relatorio_pdf", "relatorio_csv"):
            response = self.client.get(reverse(nome), {"ciclo": "2026-11"})
            self.assertEqual(response.status_code, 403, nome)

    def test_painel_mostra_totais(self):
        self.client.force_login(self.coord)
        response = self.client.get(reverse("painel"), {"ciclo": "2026-11"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FAM-0042")
        self.assertContains(response, ">2<", html=False)

    def test_relatorio_pdf(self):
        self.client.force_login(self.coord)
        response = self.client.get(reverse("relatorio_pdf"), {"ciclo": "2026-11"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_relatorio_csv(self):
        self.client.force_login(self.coord)
        response = self.client.get(reverse("relatorio_csv"), {"ciclo": "2026-11"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn("FAM-0042", response.content.decode("utf-8"))
