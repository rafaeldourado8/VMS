from django.urls import path
from .views import VehicleTypesAPIView, DetectionsByPeriodAPIView # <--- Novo import

urlpatterns = [
    # Endpoint 5.3
    path('analytics/vehicle-types/', VehicleTypesAPIView.as_view(), name='vehicle-types'),
    
    # Endpoint 5.2 (NOVO)
    path('analytics/detections-by-period/', DetectionsByPeriodAPIView.as_view(), name='detections-by-period'),
]