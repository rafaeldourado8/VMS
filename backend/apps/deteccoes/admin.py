from django.contrib import admin
from .models import Deteccao

@admin.register(Deteccao)
class DeteccaoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'camera', 'vehicle_type', 'data_hora', 'confianca')
    list_filter = ('vehicle_type', 'camera__name', 'data_hora')
    search_fields = ('placa', 'camera__name')
    ordering = ('-data_hora',)
    readonly_fields = ('created_at',)