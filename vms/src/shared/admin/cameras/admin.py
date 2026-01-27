from django.contrib import admin
from .models import Camera

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'protocol', 'is_lpr', 'is_active', 'created_at']
    list_filter = ['city', 'protocol', 'is_lpr', 'is_active']
    search_fields = ['name', 'public_id', 'city__name']
    readonly_fields = ['id', 'public_id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('id', 'public_id', 'city', 'name')
        }),
        ('Streaming', {
            'fields': ('stream_url', 'protocol')
        }),
        ('Configurações', {
            'fields': ('is_lpr', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
