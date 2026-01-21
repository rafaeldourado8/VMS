from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Camera

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_link', 'org_link', 'location', 'status_badge', 'ai_badge', 'created_at')
    list_filter = ('status', 'ai_enabled', 'owner__organization')
    search_fields = ('name', 'location', 'owner__email', 'owner__organization__name')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'stream_url_display')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'location', 'owner', 'status')
        }),
        ('Configuração', {
            'fields': ('rtsp_url', 'ai_enabled', 'stream_url_display')
        }),
        ('Metadados', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('owner', 'owner__organization')
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'organization') and request.user.organization:
            return qs.filter(owner__organization=request.user.organization)
        return qs.none()
    
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'organization') and request.user.role in ['admin', 'operator']:
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and hasattr(request.user, 'organization'):
            if obj.owner.organization == request.user.organization and request.user.role in ['admin', 'operator']:
                return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and hasattr(request.user, 'organization'):
            if obj.owner.organization == request.user.organization and request.user.role == 'admin':
                return True
        return False
    
    def owner_link(self, obj):
        url = reverse('admin:usuarios_usuario_change', args=[obj.owner.id])
        return format_html('<a href="{}">{}</a>', url, obj.owner.email)
    owner_link.short_description = 'Proprietário'
    
    def org_link(self, obj):
        if obj.owner.organization:
            url = reverse('admin:tenants_organization_change', args=[obj.owner.organization.id])
            return format_html('<a href="{}">{}</a>', url, obj.owner.organization.name)
        return '-'
    org_link.short_description = 'Organização'
    
    def status_badge(self, obj):
        colors = {'online': 'green', 'offline': 'red', 'maintenance': 'orange'}
        return format_html(
            '<span style="color:{};">● {}</span>',
            colors.get(obj.status, 'gray'), obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def ai_badge(self, obj):
        if obj.ai_enabled:
            return format_html('<span style="color:blue;">✓ IA Ativa</span>')
        return format_html('<span style="color:gray;">✗ IA Inativa</span>')
    ai_badge.short_description = 'IA'
    
    def stream_url_display(self, obj):
        if obj.rtsp_url:
            return format_html('<code>{}</code>', obj.rtsp_url)
        return '-'
    stream_url_display.short_description = 'URL do Stream'