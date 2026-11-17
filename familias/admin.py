from django.contrib import admin

from .models import Familia


@admin.register(Familia)
class FamiliaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "responsavel_nome", "qtd_membros", "ativo", "criado_em")
    list_filter = ("ativo",)
    search_fields = ("codigo", "responsavel_nome", "endereco")
    readonly_fields = ("criado_em",)
