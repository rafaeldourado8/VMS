from django.contrib import admin
from .models import CityModel

@admin.register(CityModel)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'plan', 'max_cameras', 'max_lpr_cameras', 'created_at']
    list_filter = ['plan', 'created_at']
    search_fields = ['name', 'slug']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('id', 'name', 'slug')
        }),
        ('Plano', {
            'fields': ('plan', 'max_cameras', 'max_lpr_cameras')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at')
        }),
    )
