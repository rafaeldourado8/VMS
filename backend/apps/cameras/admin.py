from .models import Camera

from django.contrib import admin

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'location', 'status', 'created_at')
    list_filter = ('status', 'owner')
    search_fields = ('name', 'location', 'owner__email')
    ordering = ('-created_at',)