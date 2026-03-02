from django.contrib import admin
from .models import NotificationPreference, NotificationLog, LoginLog


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'logged_in_at']
    list_filter = ['logged_in_at']
    search_fields = ['user__email', 'user__name', 'ip_address']
    readonly_fields = ['user', 'ip_address', 'user_agent', 'logged_in_at']
    date_hierarchy = 'logged_in_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_alerts', 'push_notifications', 'updated_at']
    list_filter = ['email_alerts', 'push_notifications']
    search_fields = ['user__email', 'user__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'category', 'title', 'sent_at', 'success']
    list_filter = ['type', 'category', 'success', 'sent_at']
    search_fields = ['user__email', 'title', 'message']
    readonly_fields = ['sent_at']
    date_hierarchy = 'sent_at'
