from django.contrib import admin
from .models import UserModel


@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "is_admin", "is_active", "created_at"]
    list_filter = ["is_admin", "is_active", "created_at"]
    search_fields = ["email", "name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    
    fieldsets = (
        ("Informações", {
            "fields": ("id", "email", "name", "password_hash")
        }),
        ("Permissões", {
            "fields": ("city_ids", "is_admin", "is_active")
        }),
        ("Datas", {
            "fields": ("created_at", "updated_at")
        }),
    )
