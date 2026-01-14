from django.contrib import admin
from .models import VehicleSearchModel

@admin.register(VehicleSearchModel)
class VehicleSearchAdmin(admin.ModelAdmin):
    list_display = ['search_criteria', 'status', 'date_range', 'created_at']
    list_filter = ['status', 'created_at', 'city_id']
    search_fields = ['plate', 'color', 'vehicle_type', 'user_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'error_message']
    actions = ['reprocess_searches']
    
    fieldsets = (
        ('Critérios de Busca', {
            'fields': ('id', 'plate', 'color', 'vehicle_type')
        }),
        ('Período', {
            'fields': ('start_date', 'end_date')
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Metadados', {
            'fields': ('city_id', 'user_id', 'created_at', 'updated_at')
        }),
    )
    
    def search_criteria(self, obj):
        criteria = []
        if obj.plate:
            criteria.append(f"🚗 {obj.plate}")
        if obj.color:
            criteria.append(f"🎨 {obj.color}")
        if obj.vehicle_type:
            criteria.append(f"🚙 {obj.vehicle_type}")
        return ' | '.join(criteria) if criteria else 'No criteria'
    search_criteria.short_description = 'Criteria'
    
    def date_range(self, obj):
        return f"{obj.start_date.strftime('%d/%m/%Y')} - {obj.end_date.strftime('%d/%m/%Y')}"
    date_range.short_description = 'Period'
    
    def reprocess_searches(self, request, queryset):
        # TODO: Reprocessar buscas
        count = queryset.filter(status='failed').update(status='pending')
        self.message_user(request, f"{count} searches marked for reprocessing")
    reprocess_searches.short_description = "Reprocess failed searches"
    
    def has_add_permission(self, request):
        return False  # Buscas são criadas via API
