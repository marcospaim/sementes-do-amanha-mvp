from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from contas.models import PerfilUsuario
from familias.forms import FamiliaForm
from familias.models import Familia

User = get_user_model()


def criar_familia(**kwargs):
    dados = {
        "codigo": "FAM-0042",
        "responsavel_nome": "Maria S.",
        "endereco": "Rua das Acácias, 120",
        "qtd_membros": 4,
    }
    dados.update(kwargs)
    return Familia.objects.create(**dados)


class FamiliaFormTests(TestCase):
    def test_codigo_duplicado_e_recusado(self):
        criar_familia()
        form = FamiliaForm(
            data={
                "codigo": "fam-0042",
                "responsavel_nome": "Outra",
                "endereco": "Rua B, 10",
                "qtd_membros": 2,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("codigo", form.errors)

    def test_nome_e_endereco_semelhantes_geram_alerta(self):
        criar_familia()
        form = FamiliaForm(
            data={
                "codigo": "FAM-0099",
                "responsavel_nome": "maria s.",
                "endereco": "RUA DAS ACÁCIAS, 120",
                "qtd_membros": 4,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertTrue(form.non_field_errors())


class FamiliaViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vol", password="senha-forte-123")

    def test_lista_exige_login(self):
        response = self.client.get(reverse("familia_lista"))
        self.assertEqual(response.status_code, 302)

    def test_cadastro_cria_familia(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("familia_nova"),
            {
                "codigo": "FAM-0100",
                "responsavel_nome": "Ana P.",
                "endereco": "Rua C, 30",
                "telefone": "",
                "qtd_membros": 3,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Familia.objects.filter(codigo="FAM-0100").exists())

    def test_busca_por_codigo(self):
        criar_familia()
        criar_familia(codigo="FAM-0043", responsavel_nome="João P.")
        self.client.force_login(self.user)
        response = self.client.get(reverse("familia_lista"), {"q": "0042"})
        self.assertContains(response, "FAM-0042")
        self.assertNotContains(response, "FAM-0043")

    def test_voluntario_nao_ve_telefone(self):
        criar_familia(telefone="(51) 99999-0000")
        self.client.force_login(self.user)
        response = self.client.get(reverse("familia_lista"))
        self.assertNotContains(response, "(51) 99999-0000")

    def test_coordenacao_ve_telefone(self):
        criar_familia(telefone="(51) 99999-0000")
        self.user.perfil.papel = PerfilUsuario.Papel.COORDENACAO
        self.user.perfil.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse("familia_lista"))
        self.assertContains(response, "(51) 99999-0000")
