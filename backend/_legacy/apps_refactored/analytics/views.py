from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services import AnalyticsService

class VehicleTypesAPIView(APIView):
    """Endpoint para distribuição de tipos de veículos com cache de 5 min."""
    permission_classes = [IsAuthenticated]
    CACHE_TIMEOUT = 300 

    def get(self, request):
        cache_key = f"analytics_types_{request.user.id}"
        data = cache.get(cache_key)

        if not data:
            service = AnalyticsService(user=request.user)
            # Converte DTOs para dicionários para a resposta
            data = [vars(dto) for dto in service.get_vehicle_type_distribution()]
            cache.set(cache_key, data, timeout=self.CACHE_TIMEOUT)

        return Response({"data": data})

class DetectionsByPeriodAPIView(APIView):
    """Endpoint para detecções temporais agrupadas."""
    permission_classes = [IsAuthenticated]
    CACHE_TIMEOUT = 300

    def get(self, request):
        period = request.query_params.get("period", "day")
        cache_key = f"analytics_period_{request.user.id}_{period}"
        data = cache.get(cache_key)

        if not data:
            service = AnalyticsService(user=request.user)
            try:
                data = [vars(dto) for dto in service.get_detections_by_period(period)]
                cache.set(cache_key, data, timeout=self.CACHE_TIMEOUT)
            except ValueError as e:
                return Response({"error": str(e)}, status=400)

        return Response({"period": period, "data": data})