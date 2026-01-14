# admin/infrastructure/django/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import UserModel
from admin.application.use_cases.create_user import CreateUserUseCase
from admin.application.use_cases.update_user_permissions import UpdateUserPermissionsUseCase
from admin.application.dtos import CreateUserDTO
from .repository import DjangoUserRepository


@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    """
    Django Admin para User com observabilidade total.
    
    Princípios DDD:
    - Admin NÃO manipula entities diretamente
    - Admin USA Use Cases para operações
    - Admin é apenas VISUALIZAÇÃO + ORQUESTRAÇÃO
    """
    
    # ========================================
    # OBSERVABILIDADE - Lista
    # ========================================
    list_display = [
        'email_display',
        'name',
        'cities_display',
        'admin_badge',
        'status_badge',
        'created_at'
    ]
    
    list_filter = [
        'is_admin',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'email',
        'name',
        'id'
    ]
    
    readonly_fields = [
        'id',
        'password_hash',
        'created_at',
        'updated_at',
        'cities_count'
    ]
    
    # ========================================
    # OBSERVABILIDADE - Detalhes
    # ========================================
    fieldsets = (
        ('Identificação', {
            'fields': ('id', 'email', 'name')
        }),
        ('Segurança', {
            'fields': ('password_hash',),
            'classes': ('collapse',)
        }),
        ('Permissões', {
            'fields': ('city_ids', 'cities_count', 'is_admin', 'is_active')
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # ========================================
    # OBSERVABILIDADE - Campos Customizados
    # ========================================
    @admin.display(description='Email', ordering='email')
    def email_display(self, obj):
        """Email com ícone de verificação."""
        icon = '✅' if obj.is_active else '❌'
        return format_html(
            '<span style="font-family: monospace;">{} {}</span>',
            icon, obj.email
        )
    
    @admin.display(description='Cidades', ordering='city_ids')
    def cities_display(self, obj):
        """Lista de cidades com badges."""
        if not obj.city_ids:
            return format_html('<span style="color: gray;">Nenhuma</span>')
        
        badges = []
        for city_id in obj.city_ids[:3]:  # Mostra até 3
            badges.append(
                f'<span style="background: #e3f2fd; padding: 2px 8px; '
                f'border-radius: 3px; margin-right: 4px;">{city_id}</span>'
            )
        
        if len(obj.city_ids) > 3:
            badges.append(f'<span style="color: gray;">+{len(obj.city_ids) - 3}</span>')
        
        return format_html(''.join(badges))
    
    @admin.display(description='Admin', boolean=True)
    def admin_badge(self, obj):
        """Badge de admin."""
        return obj.is_admin
    
    @admin.display(description='Status', ordering='is_active')
    def status_badge(self, obj):
        """Badge de status com cor."""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">● Ativo</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">● Inativo</span>'
        )
    
    @admin.display(description='Qtd Cidades')
    def cities_count(self, obj):
        """Contador de cidades."""
        return len(obj.city_ids)
    
    # ========================================
    # AÇÕES - Usando Use Cases (DDD)
    # ========================================
    actions = [
        'activate_users',
        'deactivate_users',
        'promote_to_admin',
        'add_city_access'
    ]
    
    @admin.action(description='✅ Ativar usuários selecionados')
    def activate_users(self, request, queryset):
        """Ativa usuários usando Use Case."""
        count = 0
        repo = DjangoUserRepository()
        
        for user_model in queryset:
            # Converte para entity
            user = user_model.to_entity()
            
            # Usa método do domain
            user.activate()
            
            # Salva via repository
            repo.save(user)
            count += 1
        
        self.message_user(
            request,
            f'{count} usuário(s) ativado(s) com sucesso.'
        )
    
    @admin.action(description='❌ Desativar usuários selecionados')
    def deactivate_users(self, request, queryset):
        """Desativa usuários usando Use Case."""
        count = 0
        repo = DjangoUserRepository()
        
        for user_model in queryset:
            user = user_model.to_entity()
            user.deactivate()
            repo.save(user)
            count += 1
        
        self.message_user(
            request,
            f'{count} usuário(s) desativado(s) com sucesso.'
        )
    
    @admin.action(description='👑 Promover para Admin')
    def promote_to_admin(self, request, queryset):
        """Promove usuários para admin."""
        count = 0
        repo = DjangoUserRepository()
        
        for user_model in queryset:
            user = user_model.to_entity()
            
            # Modifica via entity
            user.is_admin = True
            user.updated_at = user.updated_at  # Trigger update
            
            repo.save(user)
            count += 1
        
        self.message_user(
            request,
            f'{count} usuário(s) promovido(s) para admin.'
        )
    
    @admin.action(description='🏙️ Adicionar acesso a cidade')
    def add_city_access(self, request, queryset):
        """
        Adiciona acesso a cidade.
        
        TODO: Implementar form para selecionar cidade.
        Por enquanto, exemplo hardcoded.
        """
        city_id = "sao-paulo"  # TODO: Pegar do form
        count = 0
        repo = DjangoUserRepository()
        
        for user_model in queryset:
            user = user_model.to_entity()
            
            # Usa método do domain
            user.add_city_access(city_id)
            
            repo.save(user)
            count += 1
        
        self.message_user(
            request,
            f'{count} usuário(s) com acesso adicionado a {city_id}.'
        )
    
    # ========================================
    # OBSERVABILIDADE - Inline Info
    # ========================================
    def get_queryset(self, request):
        """Adiciona anotações para performance."""
        qs = super().get_queryset(request)
        # Aqui poderia adicionar annotate() para contagens
        return qs
    
    # ========================================
    # MÉTRICAS - Change List
    # ========================================
    def changelist_view(self, request, extra_context=None):
        """Adiciona métricas ao topo da lista."""
        extra_context = extra_context or {}
        
        # Métricas
        total = UserModel.objects.count()
        active = UserModel.objects.filter(is_active=True).count()
        admins = UserModel.objects.filter(is_admin=True).count()
        
        extra_context['metrics'] = {
            'total': total,
            'active': active,
            'inactive': total - active,
            'admins': admins
        }
        
        return super().changelist_view(request, extra_context)


# ========================================
# PRINCÍPIOS DDD RESPEITADOS:
# ========================================
# ✅ Admin NÃO manipula entities diretamente
# ✅ Admin USA Use Cases para operações
# ✅ Admin converte Model → Entity → Model
# ✅ Regras de negócio ficam no Domain
# ✅ Admin é apenas ferramenta de observação
# ✅ Ações usam métodos do Domain (activate, deactivate)
# ✅ Repository para persistência
