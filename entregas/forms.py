from django import forms

from estoque.models import Item
from familias.models import Familia

from .models import Entrega
from .services import ciclo_atual


class EntregaForm(forms.Form):
    familia = forms.ModelChoiceField(
        queryset=Familia.objects.filter(ativo=True),
        label="Família",
        empty_label="Selecione a família",
    )
    item = forms.ModelChoiceField(
        queryset=Item.objects.filter(ativo=True),
        label="Item",
        empty_label="Selecione o item",
    )
    quantidade = forms.IntegerField(
        label="Quantidade",
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={"min": 1, "inputmode": "numeric"}),
    )
    ciclo = forms.CharField(
        label="Ciclo",
        max_length=7,
        initial=ciclo_atual,
        help_text="Formato AAAA-MM. Uma família recebe uma cesta por ciclo.",
        widget=forms.TextInput(attrs={"placeholder": "2026-11"}),
    )

    def clean_ciclo(self):
        ciclo = (self.cleaned_data["ciclo"] or "").strip()
        try:
            ano, mes = ciclo.split("-")
            if len(ano) != 4 or len(mes) != 2 or not (1 <= int(mes) <= 12):
                raise ValueError
        except (ValueError, AttributeError) as exc:
            raise forms.ValidationError("Use o formato AAAA-MM, por exemplo 2026-11.") from exc
        return ciclo


class EntregaSyncForm(forms.ModelForm):
    """Validação usada pelo endpoint de sincronização offline."""

    familia_codigo = forms.CharField(max_length=12)
    origem_uuid = forms.UUIDField(required=False)

    class Meta:
        model = Entrega
        fields = ["item", "quantidade", "ciclo"]

    def clean_familia_codigo(self):
        codigo = (self.cleaned_data["familia_codigo"] or "").strip().upper()
        if not Familia.objects.filter(codigo=codigo, ativo=True).exists():
            raise forms.ValidationError("Família não encontrada para o código informado.")
        return codigo
