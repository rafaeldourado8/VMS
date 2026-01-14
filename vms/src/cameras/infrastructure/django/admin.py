from django.contrib import admin
from .models import CameraModel

@admin.register(CameraModel)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'lpr_status', 'status', 'city_id', 'created_at']
    list_filter = ['type', 'lpr_enabled', 'status', 'created_at']
    search_fields = ['name', 'stream_url']
    readonly_fields = ['id', 'type', 'lpr_enabled', 'created_at', 'updated_at']
    actions = ['activate_cameras', 'deactivate_cameras']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('id', 'name', 'city_id')
        }),
        ('Configuração', {
            'fields': ('stream_url', 'type', 'lpr_enabled', 'status')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def lpr_status(self, obj):
        return '✅ LPR Ativo' if obj.lpr_enabled else '❌ Sem LPR'
    lpr_status.short_description = 'LPR'
    
    def activate_cameras(self, request, queryset):
        count = queryset.update(status='active')
        self.message_user(request, f"{count} câmeras ativadas")
    activate_cameras.short_description = "Ativar câmeras selecionadas"
    
    def deactivate_cameras(self, request, queryset):
        count = queryset.update(status='inactive')
        self.message_user(request, f"{count} câmeras desativadas")
    deactivate_cameras.short_description = "Desativar câmeras selecionadas"
