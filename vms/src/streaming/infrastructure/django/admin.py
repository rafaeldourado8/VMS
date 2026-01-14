from django.contrib import admin
from .models import StreamModel

@admin.register(StreamModel)
class StreamAdmin(admin.ModelAdmin):
    list_display = ['camera_id', 'status', 'started_at', 'hls_url_short']
    list_filter = ['status', 'created_at']
    search_fields = ['camera_id', 'hls_url']
    readonly_fields = ['id', 'hls_url', 'created_at', 'updated_at']
    actions = ['stop_streams']
    
    fieldsets = (
        ('Informações', {
            'fields': ('id', 'camera_id', 'status')
        }),
        ('Stream', {
            'fields': ('hls_url', 'started_at')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def hls_url_short(self, obj):
        return obj.hls_url[:50] + '...' if len(obj.hls_url) > 50 else obj.hls_url
    hls_url_short.short_description = 'HLS URL'
    
    def stop_streams(self, request, queryset):
        count = queryset.update(status='stopped')
        self.message_user(request, f"{count} streams parados")
    stop_streams.short_description = "Parar streams selecionados"
