from django.contrib import admin
from .models import DetectionModel

@admin.register(DetectionModel)
class DetectionAdmin(admin.ModelAdmin):
    list_display = ['plate', 'confidence_display', 'camera_id', 'detected_at', 'is_high_confidence']
    list_filter = ['confidence', 'detected_at', 'city_id']
    search_fields = ['plate', 'camera_id']
    readonly_fields = ['id', 'camera_id', 'plate', 'confidence', 'image_url', 'detected_at', 'city_id', 'created_at']
    
    fieldsets = (
        ('Detecção', {
            'fields': ('id', 'plate', 'confidence', 'image_url')
        }),
        ('Localização', {
            'fields': ('camera_id', 'city_id', 'detected_at')
        }),
        ('Metadados', {
            'fields': ('created_at',)
        }),
    )
    
    def confidence_display(self, obj):
        return f"{obj.confidence:.2%}"
    confidence_display.short_description = 'Confidence'
    
    def is_high_confidence(self, obj):
        return '✅' if obj.confidence >= 0.9 else '⚠️'
    is_high_confidence.short_description = 'High Conf'
    
    def has_add_permission(self, request):
        return False  # Detecções são criadas automaticamente
