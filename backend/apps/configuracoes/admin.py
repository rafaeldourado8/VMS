from django.contrib import admin
from .models import ConfiguracaoGlobal

@admin.register(ConfiguracaoGlobal)
class ConfiguracaoGlobalAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'notificacoes_habilitadas', 'em_manutencao', 'updated_at')
    
    # Impede que administradores criem NOVAS instâncias (apenas edição)
    def has_add_permission(self, request):
        return False
    
    # Impede que administradores DELETEM a instância
    def has_delete_permission(self, request, obj=None):
        return False