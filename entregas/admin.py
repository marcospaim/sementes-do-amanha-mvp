from django.contrib import admin

from .models import Entrega


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ("familia", "item", "quantidade", "ciclo", "usuario_registro", "sincronizado_em")
    list_filter = ("ciclo", "item")
    search_fields = ("familia__codigo", "familia__responsavel_nome")
    readonly_fields = ("origem_uuid", "data")
