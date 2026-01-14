from django.contrib import admin
from .models import Organization, Subscription
from apps.usuarios.models import Usuario

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'database_name', 'is_active', 'user_count', 'created_at']
    search_fields = ['name', 'slug']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at']
    
    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = 'Usuários'

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['organization', 'plan', 'recording_days', 'max_cameras', 'max_users', 'is_active', 'started_at']
    list_filter = ['plan', 'is_active', 'started_at']
    search_fields = ['organization__name']
    readonly_fields = ['recording_days', 'max_cameras', 'max_users', 'max_clips', 'max_concurrent_streams', 'started_at']
    
    fieldsets = (
        ('Organização', {
            'fields': ('organization', 'plan', 'is_active')
        }),
        ('Limites (Auto-calculados)', {
            'fields': ('recording_days', 'max_cameras', 'max_users', 'max_clips', 'max_concurrent_streams'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('started_at', 'expires_at')
        }),
    )
