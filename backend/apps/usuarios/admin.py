from django.contrib import admin
from .models import Usuario

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
        ('Organização (OBRIGATÓRIO)', {
            'fields': ('organization', 'role', 'plan'),
            'description': 'Selecione a organização antes de salvar'
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
    
    def save_model(self, request, obj, form, change):
        if not change:  # Novo usuário
            # Validar email
            if not obj.email.endswith('@gtvision.com.br'):
                from django.contrib import messages
                messages.error(request, 'Email deve ser @gtvision.com.br')
                return
            # Hash da senha
            if 'password' in form.changed_data and form.cleaned_data['password']:
                obj.set_password(form.cleaned_data['password'])
            else:
                obj.set_password('gtvision123')  # Senha padrão
        else:  # Editando
            if 'password' in form.changed_data and form.cleaned_data['password']:
                obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)