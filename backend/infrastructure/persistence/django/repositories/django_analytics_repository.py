from typing import Dict

from django.db.models import Count, Q
from django.db.models.functions import Extract

from apps.cameras.models import Camera
from apps.deteccoes.models import Deteccao
from domain.analytics import AnalyticsRepository, Period

class DjangoAnalyticsRepository(AnalyticsRepository):
    """Implementação Django otimizada do repositório de analytics"""
    
    def get_detection_count(self, period: Period, camera_id: int = None) -> int:
        """Conta detecções no período com query otimizada"""
        queryset = Deteccao.objects.filter(
            timestamp__gte=period.start_date,
            timestamp__lte=period.end_date
        )
        
        if camera_id:
            queryset = queryset.filter(camera_id=camera_id)
        
        return queryset.count()
    
    def get_active_cameras_count(self) -> int:
        """Conta câmeras ativas"""
        return Camera.objects.filter(status='online').count()
    
    def get_detections_by_camera(self, period: Period) -> Dict[int, int]:
        """Detecções agrupadas por câmera com query otimizada"""
        results = Deteccao.objects.filter(
            timestamp__gte=period.start_date,
            timestamp__lte=period.end_date
        ).values('camera_id').annotate(
            count=Count('id')
        ).order_by('camera_id')
        
        return {item['camera_id']: item['count'] for item in results}
    
    def get_detections_by_hour(self, period: Period) -> Dict[int, int]:
        """Detecções agrupadas por hora com query otimizada"""
        results = Deteccao.objects.filter(
            timestamp__gte=period.start_date,
            timestamp__lte=period.end_date
        ).annotate(
            hour=Extract('timestamp', 'hour')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')
        
        return {item['hour']: item['count'] for item in results}