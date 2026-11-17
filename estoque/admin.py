from django.contrib import admin

from .models import Doacao, Doador, Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("nome", "unidade", "estoque_atual", "estoque_minimo", "ativo")
    list_filter = ("ativo", "unidade")
    search_fields = ("nome",)


@admin.register(Doador)
class DoadorAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "contato")
    list_filter = ("tipo",)
    search_fields = ("nome",)


@admin.register(Doacao)
class DoacaoAdmin(admin.ModelAdmin):
    list_display = ("item", "quantidade", "doador", "data", "usuario_registro")
    list_filter = ("item", "data")
    search_fields = ("item__nome", "doador__nome")
    readonly_fields = ("origem_uuid", "criado_em")
