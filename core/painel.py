import csv
import io
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from contas.permissoes import coordenacao_required
from entregas.models import Entrega
from entregas.services import ciclo_atual
from estoque.models import Item


def _dados_ciclo(ciclo):
    entregas = Entrega.objects.filter(ciclo=ciclo).select_related("familia", "item")
    return {
        "ciclo": ciclo,
        "entregas": entregas,
        "familias_atendidas": entregas.values("familia").distinct().count(),
        "total_cestas": entregas.aggregate(total=Sum("quantidade"))["total"] or 0,
        "itens": Item.objects.filter(ativo=True),
    }


@login_required
@coordenacao_required
def painel(request):
    ciclo = (request.GET.get("ciclo") or ciclo_atual()).strip()
    contexto = _dados_ciclo(ciclo)
    return render(request, "painel/painel.html", contexto)


@login_required
@coordenacao_required
def relatorio_csv(request):
    ciclo = (request.GET.get("ciclo") or ciclo_atual()).strip()
    resposta = HttpResponse(content_type="text/csv; charset=utf-8")
    resposta["Content-Disposition"] = f'attachment; filename="entregas-{ciclo}.csv"'
    resposta.write("\ufeff")
    escritor = csv.writer(resposta, delimiter=";")
    escritor.writerow(["Ciclo", "Família", "Responsável", "Item", "Quantidade", "Registrado em"])
    for entrega in Entrega.objects.filter(ciclo=ciclo).select_related("familia", "item"):
        escritor.writerow(
            [
                entrega.ciclo,
                entrega.familia.codigo,
                entrega.familia.responsavel_nome,
                entrega.item.nome,
                entrega.quantidade,
                timezone.localtime(entrega.data).strftime("%d/%m/%Y %H:%M"),
            ]
        )
    return resposta


@login_required
@coordenacao_required
def relatorio_pdf(request):
    ciclo = (request.GET.get("ciclo") or ciclo_atual()).strip()
    dados = _dados_ciclo(ciclo)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4
    y = altura - 20 * mm

    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(20 * mm, y, "Instituto Sementes do Amanhã")
    y -= 7 * mm
    pdf.setFont("Helvetica", 11)
    pdf.drawString(20 * mm, y, f"Relatório do ciclo {ciclo}")
    pdf.drawString(20 * mm, y - 5 * mm, f"Emitido em {datetime.now():%d/%m/%Y %H:%M}")
    y -= 16 * mm

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(20 * mm, y, f"Famílias atendidas: {dados['familias_atendidas']}")
    pdf.drawString(90 * mm, y, f"Total de cestas: {dados['total_cestas']}")
    y -= 10 * mm

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(20 * mm, y, "Família")
    pdf.drawString(50 * mm, y, "Responsável")
    pdf.drawString(120 * mm, y, "Item")
    pdf.drawString(165 * mm, y, "Qtd.")
    y -= 6 * mm

    pdf.setFont("Helvetica", 9)
    for entrega in dados["entregas"]:
        if y < 25 * mm:
            pdf.showPage()
            y = altura - 20 * mm
            pdf.setFont("Helvetica", 9)
        pdf.drawString(20 * mm, y, entrega.familia.codigo)
        pdf.drawString(50 * mm, y, entrega.familia.responsavel_nome[:38])
        pdf.drawString(120 * mm, y, entrega.item.nome[:26])
        pdf.drawRightString(175 * mm, y, str(entrega.quantidade))
        y -= 5 * mm

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    resposta = HttpResponse(buffer.read(), content_type="application/pdf")
    resposta["Content-Disposition"] = f'attachment; filename="relatorio-{ciclo}.pdf"'
    return resposta
