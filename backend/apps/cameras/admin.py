from django.contrib import admin
from .models import Camera

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'location', 'status', 'created_at')
    list_filter = ('status', 'owner')
    search_fields = ('name', 'location', 'owner__email')
    ordering = ('-created_at',)
    
    def get_inline_instances(self, request, obj=None):
        inlines = super().get_inline_instances(request, obj)
        try:
            from apps.timeline.admin import CameraRetentionInline
            inlines.append(CameraRetentionInline(self.model, self.admin_site))
        except ImportError:
            pass
        return inlines