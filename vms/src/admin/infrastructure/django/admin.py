from django.contrib import admin
from django.utils.html import format_html
from .models import UserModel
from admin.application.use_cases.update_user_permissions import UpdateUserPermissionsUseCase
from admin.infrastructure.django.repository import DjangoUserRepository


@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "is_admin", "is_active", "cities_count", "created_at"]
    list_filter = ["is_admin", "is_active", "created_at"]
    search_fields = ["email", "name"]
    readonly_fields = ["id", "password_hash", "created_at", "updated_at"]
    actions = ["activate_users", "deactivate_users", "promote_to_admin"]
    
    fieldsets = (
        ("Informações", {
            "fields": ("id", "email", "name")
        }),
        ("Segurança", {
            "fields": ("password_hash", "is_active")
        }),
        ("Permissões", {
            "fields": ("is_admin", "city_ids")
        }),
        ("Datas", {
            "fields": ("created_at", "updated_at")
        }),
    )
    
    def cities_count(self, obj):
        """Número de cidades com acesso."""
        count = len(obj.city_ids)
        if obj.is_admin:
            return format_html('<span style="color: green;"><b>ADMIN (todas)</b></span>')
        return format_html(f'<span>{count} cidade(s)</span>')
    cities_count.short_description = "Cidades"
    
    def activate_users(self, request, queryset):
        """Ativa usuários selecionados."""
        repo = DjangoUserRepository()
        for user_model in queryset:
            user = repo.find_by_id(user_model.id)
            if user:
                user.activate()
                repo.save(user)
        self.message_user(request, f"{queryset.count()} usuário(s) ativado(s)")
    activate_users.short_description = "Ativar usuários selecionados"
    
    def deactivate_users(self, request, queryset):
        """Desativa usuários selecionados."""
        repo = DjangoUserRepository()
        for user_model in queryset:
            user = repo.find_by_id(user_model.id)
            if user:
                user.deactivate()
                repo.save(user)
        self.message_user(request, f"{queryset.count()} usuário(s) desativado(s)")
    deactivate_users.short_description = "Desativar usuários selecionados"
    
    def promote_to_admin(self, request, queryset):
        """Promove usuários a admin."""
        repo = DjangoUserRepository()
        for user_model in queryset:
            user = repo.find_by_id(user_model.id)
            if user and not user.is_admin:
                user.is_admin = True
                repo.save(user)
        self.message_user(request, f"{queryset.count()} usuário(s) promovido(s) a admin")
    promote_to_admin.short_description = "Promover a Admin"
