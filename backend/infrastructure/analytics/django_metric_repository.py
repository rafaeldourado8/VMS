from .mappers.metric_mapper import MetricMapper
from datetime import datetime
from typing import List, Dict, Any

from django.db.models import Avg, Sum, Count, Max, Min

from ...domain.analytics.entities.metric import Metric, MetricType
from ...domain.analytics.repositories.metric_repository import MetricRepository
from apps.detection.models import Detection
from apps.monitoring.models import Camera

class DjangoMetricRepository(MetricRepository):
    """Implementação Django do repositório de métricas."""
    
    def save(self, metric: Metric) -> Metric:
        """Salva uma métrica (implementação futura)."""
        # Para MVP, métricas são calculadas em tempo real
        return metric
    
    def get_metrics_by_type(
        self, 
        metric_type: MetricType,
        start_date: datetime,
        end_date: datetime
    ) -> List[Metric]:
        """Busca métricas por tipo e período."""
        if metric_type == MetricType.CAMERA_STATUS:
            return self._get_camera_metrics(start_date, end_date)
        elif metric_type == MetricType.DETECTION_COUNT:
            return self._get_detection_metrics(start_date, end_date)
        return []
    
    def get_aggregated_metrics(
        self,
        metric_type: MetricType,
        start_date: datetime,
        end_date: datetime,
        aggregation: str = "avg"
    ) -> Dict[str, Any]:
        """Retorna métricas agregadas."""
        if metric_type == MetricType.CAMERA_STATUS:
            return self._get_camera_aggregated(aggregation)
        elif metric_type == MetricType.DETECTION_COUNT:
            return self._get_detection_aggregated(start_date, end_date, aggregation)
        return {}
    
    def _get_camera_metrics(self, start_date: datetime, end_date: datetime) -> List[Metric]:
        """Métricas de status das câmeras."""
        cameras = Camera.objects.all()
        metrics = []
        
        for camera in cameras:
            metric = Metric(
                id=None,
                type=MetricType.CAMERA_STATUS,
                value=1.0 if camera.ativo else 0.0,
                metadata={"camera_id": camera.id, "camera_name": camera.nome},
                timestamp=datetime.now()
            )
            metrics.append(metric)
        
        return metrics
    
    def _get_detection_metrics(self, start_date: datetime, end_date: datetime) -> List[Metric]:
        """Métricas de detecções."""
        detections = Detection.objects.filter(
            timestamp__range=[start_date, end_date]
        )
        
        metrics = []
        for detection in detections:
            metric = Metric(
                id=None,
                type=MetricType.DETECTION_COUNT,
                value=1.0,
                metadata={"detection_id": detection.id, "camera_id": detection.camera_id},
                timestamp=detection.timestamp
            )
            metrics.append(metric)
        
        return metrics
    
    def _get_camera_aggregated(self, aggregation: str) -> Dict[str, Any]:
        """Métricas agregadas de câmeras."""
        total_cameras = Camera.objects.count()
        active_cameras = Camera.objects.filter(ativo=True).count()
        
        return {
            "total": total_cameras,
            "active": active_cameras,
            "inactive": total_cameras - active_cameras,
            "uptime_percentage": (active_cameras / total_cameras * 100) if total_cameras > 0 else 0
        }
    
    def _get_detection_aggregated(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        aggregation: str
    ) -> Dict[str, Any]:
        """Métricas agregadas de detecções."""
        detections = Detection.objects.filter(
            timestamp__range=[start_date, end_date]
        )
        
        total = detections.count()
        by_camera = detections.values('camera_id').annotate(count=Count('id'))
        
        return {
            "total": total,
            "by_camera": list(by_camera),
            "period_days": (end_date - start_date).days,
            "avg_per_day": total / max((end_date - start_date).days, 1)
        }