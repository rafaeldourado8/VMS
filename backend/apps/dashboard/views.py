from rest_framework.response import Response
from rest_framework.views import APIView
from apps.cameras.models import Camera
from apps.deteccoes.models import Deteccao
from django.utils import timezone
from datetime import timedelta

class DashboardStatsAPIView(APIView):
    """
    Endpoint mínimo para Dashboard - MVP (sem autenticação)
    """

    def get(self, request):
        # Stats básicas para o MVP
        total_cameras = Camera.objects.count()
        active_cameras = Camera.objects.filter(status='online').count()
        
        # Detecções das últimas 24h
        last_24h = timezone.now() - timedelta(hours=24)
        recent_detections = Deteccao.objects.filter(timestamp__gte=last_24h).count()
        
        return Response({
            "total_cameras": total_cameras,
            "active_cameras": active_cameras,
            "total_detections": recent_detections,
            "period": "24h"
        })