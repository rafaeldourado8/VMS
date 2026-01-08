from .models import Mensagem

from django.contrib import admin

@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ("autor", "timestamp", "respondido_por_admin")
    list_filter = ("autor", "respondido_por_admin")
    search_fields = ("conteudo", "autor__email")
    readonly_fields = ("autor", "timestamp", "conteudo", "respondido_por_admin")

    # Admin não deve criar mensagens por aqui, apenas ler
    def has_add_permission(self, request):
        return False
