from .models import Deteccao

from django.contrib import admin

@admin.register(Deteccao)
class DeteccaoAdmin(admin.ModelAdmin):
    list_display = ('plate', 'camera', 'vehicle_type', 'timestamp', 'confidence')
    list_filter = ('vehicle_type', 'camera__name', 'timestamp')
    search_fields = ('plate', 'camera__name')
    ordering = ('-timestamp',)
    readonly_fields = ('created_at',)