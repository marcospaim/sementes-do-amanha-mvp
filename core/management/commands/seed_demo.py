from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from contas.models import PerfilUsuario
from entregas.services import registrar_entrega
from estoque.models import Doacao, Doador, Item
from estoque.services import registrar_doacao
from familias.models import Familia

User = get_user_model()

SENHA_DEMO = "demo-sementes-123"


class Command(BaseCommand):
    help = "Cria dados fictícios para demonstração e validação do MVP."

    def handle(self, *args, **options):
        coord, _ = User.objects.get_or_create(
            username="coordenacao", defaults={"first_name": "Mariana", "last_name": "Alves"}
        )
        coord.set_password(SENHA_DEMO)
        coord.save()
        coord.perfil.papel = PerfilUsuario.Papel.COORDENACAO
        coord.perfil.save()

        vol, _ = User.objects.get_or_create(
            username="voluntario", defaults={"first_name": "Cláudia", "last_name": "Santos"}
        )
        vol.set_password(SENHA_DEMO)
        vol.save()
        vol.perfil.papel = PerfilUsuario.Papel.VOLUNTARIO
        vol.perfil.save()

        cestas, _ = Item.objects.get_or_create(
            nome="Cesta básica", defaults={"unidade": Item.Unidade.CESTA, "estoque_minimo": 10}
        )
        leite, _ = Item.objects.get_or_create(
            nome="Leite em pó", defaults={"unidade": Item.Unidade.UNIDADE, "estoque_minimo": 5}
        )

        doador, _ = Doador.objects.get_or_create(nome="Mercado Central (fictício)")

        familias = [
            ("FAM-0041", "João Pereira", "Rua das Palmeiras, 45", 3),
            ("FAM-0042", "Maria Silva", "Rua das Acácias, 120", 4),
            ("FAM-0043", "Ana Souza", "Travessa do Campo, 8", 2),
        ]
        for codigo, nome, endereco, membros in familias:
            Familia.objects.get_or_create(
                codigo=codigo,
                defaults={
                    "responsavel_nome": nome,
                    "endereco": endereco,
                    "qtd_membros": membros,
                },
            )

        if not Doacao.objects.exists():
            registrar_doacao(
                item=cestas,
                quantidade=50,
                data=timezone.localdate(),
                usuario=coord,
                doador=doador,
                observacao="Carga inicial de demonstração",
            )
            registrar_doacao(
                item=leite,
                quantidade=30,
                data=timezone.localdate(),
                usuario=coord,
                doador=doador,
            )

        ciclo = timezone.localdate().strftime("%Y-%m")
        familia_demo = Familia.objects.get(codigo="FAM-0042")
        if not familia_demo.entregas.filter(ciclo=ciclo).exists():
            registrar_entrega(
                familia=familia_demo,
                item=cestas,
                quantidade=1,
                ciclo=ciclo,
                usuario=vol,
            )

        self.stdout.write(self.style.SUCCESS("Dados de demonstração criados."))
        self.stdout.write(f"Coordenação: coordenacao / {SENHA_DEMO}")
        self.stdout.write(f"Voluntário:  voluntario / {SENHA_DEMO}")
