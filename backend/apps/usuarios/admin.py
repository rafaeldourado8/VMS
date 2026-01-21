from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'org_link', 'role_badge', 'plan_badge', 'status_badge', 'last_login')
    list_filter = ('role', 'plan', 'is_active', 'is_staff', 'organization')
    search_fields = ('email', 'name', 'organization__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_login', 'id')
    
    fieldsets = (
        ('Autenticação', {
            'fields': ('email', 'password')
        }),
        ('Informações Pessoais', {
            'fields': ('name',)
        }),
        ('Organização', {
            'fields': ('organization', 'role', 'plan')
        }),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('id', 'created_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Criar Usuário', {
            'fields': ('email', 'password1', 'password2', 'name', 'organization', 'role', 'plan')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('organization')
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'organization') and request.user.organization:
            return qs.filter(organization=request.user.organization)
        return qs.none()
    
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'organization') and request.user.role == 'admin':
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and hasattr(request.user, 'organization'):
            if request.user.organization == obj.organization and request.user.role == 'admin':
                return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and hasattr(request.user, 'organization'):
            if request.user.organization == obj.organization and request.user.role == 'admin':
                return True
        return False
    
    def org_link(self, obj):
        if obj.organization:
            url = reverse('admin:tenants_organization_change', args=[obj.organization.id])
            return format_html('<a href="{}">{}</a>', url, obj.organization.name)
        return '-'
    org_link.short_description = 'Organização'
    
    def role_badge(self, obj):
        colors = {'admin': 'red', 'operator': 'blue', 'viewer': 'gray'}
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; border-radius:3px; font-size:11px;">{}</span>',
            colors.get(obj.role, 'gray'), obj.get_role_display()
        )
    role_badge.short_description = 'Função'
    
    def plan_badge(self, obj):
        colors = {'basic': 'green', 'pro': 'orange', 'premium': 'purple'}
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; border-radius:3px; font-size:11px;">{}</span>',
            colors.get(obj.plan, 'gray'), obj.get_plan_display().upper()
        )
    plan_badge.short_description = 'Plano'
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color:green;">● Ativo</span>')
        return format_html('<span style="color:red;">● Inativo</span>')
    status_badge.short_description = 'Status'