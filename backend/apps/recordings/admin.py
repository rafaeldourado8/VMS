from django.contrib import admin
from .models import Recording

@admin.register(Recording)
class RecordingAdmin(admin.ModelAdmin):
    list_display = ['camera_id', 'date', 'file_name', 'size_mb', 'duration_min', 'is_valid']
    list_filter = ['date', 'is_valid', 'camera_id']
    search_fields = ['file_name', 'camera_id']
