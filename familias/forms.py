from django import forms

from .models import Familia


class FamiliaForm(forms.ModelForm):
    class Meta:
        model = Familia
        fields = ["codigo", "responsavel_nome", "endereco", "telefone", "qtd_membros"]
        labels = {
            "codigo": "Código da família",
            "responsavel_nome": "Nome do responsável",
            "endereco": "Endereço",
            "telefone": "Telefone (opcional)",
            "qtd_membros": "Quantidade de membros",
        }
        widgets = {
            "codigo": forms.TextInput(
                attrs={"placeholder": "FAM-0042", "autocomplete": "off", "autofocus": True}
            ),
            "responsavel_nome": forms.TextInput(attrs={"autocomplete": "name"}),
            "endereco": forms.TextInput(attrs={"autocomplete": "street-address"}),
            "telefone": forms.TextInput(
                attrs={"placeholder": "(51) 90000-0000", "autocomplete": "tel"}
            ),
            "qtd_membros": forms.NumberInput(attrs={"min": 1, "inputmode": "numeric"}),
        }

    def clean_codigo(self):
        codigo = (self.cleaned_data["codigo"] or "").strip().upper()
        if not codigo:
            raise forms.ValidationError("Informe o código da família.")
        existentes = Familia.objects.filter(codigo=codigo)
        if self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise forms.ValidationError("Já existe uma família com este código.")
        return codigo

    def clean(self):
        dados = super().clean()
        nome = (dados.get("responsavel_nome") or "").strip()
        endereco = (dados.get("endereco") or "").strip()
        if nome and endereco:
            semelhantes = Familia.objects.filter(ativo=True)
            if self.instance.pk:
                semelhantes = semelhantes.exclude(pk=self.instance.pk)
            for existente in semelhantes:
                if (
                    existente.responsavel_nome.casefold() == nome.casefold()
                    and existente.endereco.casefold() == endereco.casefold()
                ):
                    raise forms.ValidationError(
                        "Já existe uma família com este nome de responsável e endereço. "
                        "Confira o cadastro antes de gravar."
                    )
        return dados
