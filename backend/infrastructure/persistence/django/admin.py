from django.contrib import admin
from infrastructure.persistence.django.models import SectorModel, AuditLogModel

@admin.register(SectorModel)
class SectorAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']

@admin.register(AuditLogModel)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource', 'ip_address', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__email', 'resource']
    readonly_fields = ['user', 'action', 'resource', 'ip_address', 'timestamp', 'details']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
