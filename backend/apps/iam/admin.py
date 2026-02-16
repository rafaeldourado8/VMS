from django.contrib import admin
from .models import IAMPermission, IAMRule, UserPermissions, TenantIsolation

@admin.register(IAMPermission)
class IAMPermissionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'resource', 'created_at']
    list_filter = ['resource']
    search_fields = ['code', 'name']

@admin.register(IAMRule)
class IAMRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

@admin.register(UserPermissions)
class UserPermissionsAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__email', 'user__name']

@admin.register(TenantIsolation)
class TenantIsolationAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource_type', 'resource_id', 'can_read', 'can_write', 'can_delete']
    list_filter = ['resource_type', 'can_read', 'can_write', 'can_delete']
    search_fields = ['user__email', 'resource_type']
