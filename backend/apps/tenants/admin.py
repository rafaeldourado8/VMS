from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import Organization, Subscription

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'database_name', 'status_badge', 'users_count', 'cameras_count', 'created_at']
    search_fields = ['name', 'slug']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at', 'slug', 'database_name', 'stats_display']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'slug', 'database_name', 'is_active')
        }),
        ('Estatísticas', {
            'fields': ('stats_display',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            _users_count=Count('users', distinct=True),
            _cameras_count=Count('cameras', distinct=True)
        )
        if not request.user.is_superuser:
            if hasattr(request.user, 'organization'):
                return qs.filter(id=request.user.organization.id)
            return qs.none()
        return qs
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color:green;">● Ativa</span>')
        return format_html('<span style="color:red;">● Inativa</span>')
    status_badge.short_description = 'Status'
    
    def users_count(self, obj):
        return obj._users_count
    users_count.short_description = 'Usuários'
    users_count.admin_order_field = '_users_count'
    
    def cameras_count(self, obj):
        return obj._cameras_count
    cameras_count.short_description = 'Câmeras'
    cameras_count.admin_order_field = '_cameras_count'
    
    def stats_display(self, obj):
        if obj.pk:
            return format_html(
                '<strong>Usuários:</strong> {}<br>'
                '<strong>Câmeras:</strong> {}<br>'
                '<strong>Detecções (30d):</strong> {}',
                obj.users.count(),
                obj.cameras.count(),
                obj.detections.filter(created_at__gte=timezone.now() - timedelta(days=30)).count() if hasattr(obj, 'detections') else 0
            )
        return '-'
    stats_display.short_description = 'Estatísticas'

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['organization', 'plan_badge', 'limits_display', 'status_badge', 'started_at', 'expires_at']
    list_filter = ['plan', 'is_active', 'started_at']
    search_fields = ['organization__name']
    readonly_fields = ['recording_days', 'max_cameras', 'max_users', 'max_clips', 'max_concurrent_streams', 'started_at']
    
    fieldsets = (
        ('Organização', {
            'fields': ('organization', 'plan', 'is_active')
        }),
        ('Limites (Auto-calculados)', {
            'fields': ('recording_days', 'max_cameras', 'max_users', 'max_clips', 'max_concurrent_streams')
        }),
        ('Período', {
            'fields': ('started_at', 'expires_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('organization')
        if not request.user.is_superuser:
            if hasattr(request.user, 'organization'):
                return qs.filter(organization=request.user.organization)
            return qs.none()
        return qs
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def plan_badge(self, obj):
        colors = {'basic': 'green', 'pro': 'orange', 'premium': 'purple'}
        return format_html(
            '<span style="background:{}; color:white; padding:5px 10px; border-radius:3px; font-weight:bold;">{}</span>',
            colors.get(obj.plan, 'gray'), obj.get_plan_display().upper()
        )
    plan_badge.short_description = 'Plano'
    
    def limits_display(self, obj):
        return format_html(
            '<small>{} dias | {} cams | {} users</small>',
            obj.recording_days, obj.max_cameras, obj.max_users
        )
    limits_display.short_description = 'Limites'
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color:green;">● Ativa</span>')
        return format_html('<span style="color:red;">● Inativa</span>')
    status_badge.short_description = 'Status'

from django.utils import timezone
from datetime import timedelta
