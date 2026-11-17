from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from estoque.models import Item
from familias.models import Familia

from .models import Entrega
from .services import DuplicidadeError, EstoqueInsuficienteError, registrar_entrega


class EntregaSyncSerializer(serializers.Serializer):
    origem_uuid = serializers.UUIDField()
    familia_codigo = serializers.CharField(max_length=12)
    item = serializers.IntegerField()
    quantidade = serializers.IntegerField(min_value=1)
    ciclo = serializers.RegexField(r"^\d{4}-(0[1-9]|1[0-2])$")

    def validate_familia_codigo(self, valor):
        return (valor or "").strip().upper()


class SincronizarEntregaView(APIView):
    """Recebe registros feitos offline. Idempotente por origem_uuid."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EntregaSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data

        familia = Familia.objects.filter(codigo=dados["familia_codigo"], ativo=True).first()
        if familia is None:
            return Response(
                {"detail": "Família não encontrada para o código informado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item = Item.objects.filter(pk=dados["item"], ativo=True).first()
        if item is None:
            return Response(
                {"detail": "Item não encontrado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existente = Entrega.objects.filter(origem_uuid=dados["origem_uuid"]).first()
        if existente:
            return Response(
                {"status": "sincronizado", "entrega_id": existente.pk},
                status=status.HTTP_200_OK,
            )

        try:
            entrega = registrar_entrega(
                familia=familia,
                item=item,
                quantidade=dados["quantidade"],
                ciclo=dados["ciclo"],
                usuario=request.user,
                origem_uuid=dados["origem_uuid"],
                sincronizado=True,
            )
        except DuplicidadeError as exc:
            return Response(
                {"detail": str(exc), "codigo": "duplicidade"},
                status=status.HTTP_409_CONFLICT,
            )
        except EstoqueInsuficienteError as exc:
            return Response(
                {"detail": str(exc), "codigo": "estoque_insuficiente"},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"status": "sincronizado", "entrega_id": entrega.pk},
            status=status.HTTP_201_CREATED,
        )
