from .models import Usuario

from django.contrib import admin

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'organization', 'role', 'plan', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'plan', 'is_active', 'is_staff', 'organization')
    search_fields = ('email', 'name', 'organization__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_login')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('email', 'name', 'password')
        }),
        ('Organização', {
            'fields': ('organization', 'role', 'plan')
        }),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Datas', {
            'fields': ('created_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'organization') and request.user.organization:
            return qs.filter(organization=request.user.organization)
        return qs.none()