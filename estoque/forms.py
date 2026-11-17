from django import forms
from django.utils import timezone

from .models import Doacao, Doador, Item


class DoacaoForm(forms.ModelForm):
    class Meta:
        model = Doacao
        fields = ["doador", "item", "quantidade", "data", "observacao"]
        labels = {
            "doador": "Doador (opcional)",
            "item": "Item",
            "quantidade": "Quantidade",
            "data": "Data da doação",
            "observacao": "Observação (opcional)",
        }
        widgets = {
            "data": forms.DateInput(attrs={"type": "date"}),
            "quantidade": forms.NumberInput(attrs={"min": 1, "inputmode": "numeric"}),
            "observacao": forms.TextInput(attrs={"maxlength": 200}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item"].queryset = Item.objects.filter(ativo=True)
        self.fields["doador"].queryset = Doador.objects.all()
        self.fields["data"].initial = timezone.localdate()

    def clean_quantidade(self):
        quantidade = self.cleaned_data["quantidade"]
        if quantidade < 1:
            raise forms.ValidationError("A quantidade deve ser maior que zero.")
        return quantidade
