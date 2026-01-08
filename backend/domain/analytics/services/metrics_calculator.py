from ..entities.dashboard import Dashboard
from ..entities.metric import Metric
from ..repositories.analytics_repository import AnalyticsRepository
from ..value_objects.period import Period
from typing import List

class MetricsCalculator:
    """Serviço de domínio para calcular métricas"""
    
    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository
    
    def calculate_dashboard_metrics(self, period: Period) -> Dashboard:
        """Calcula métricas do dashboard"""
        
        metrics = []
        
        # Total de detecções
        total_detections = self.repository.get_detection_count(period)
        metrics.append(Metric(
            name="total_detections",
            value=float(total_detections),
            period=period,
            metadata={"type": "count"}
        ))
        
        # Câmeras ativas
        active_cameras = self.repository.get_active_cameras_count()
        metrics.append(Metric(
            name="active_cameras",
            value=float(active_cameras),
            period=period,
            metadata={"type": "count"}
        ))
        
        # Taxa de detecções por hora
        if period.duration_hours() > 0:
            detection_rate = total_detections / period.duration_hours()
            metrics.append(Metric(
                name="detection_rate_per_hour",
                value=detection_rate,
                period=period,
                metadata={"type": "rate", "unit": "per_hour"}
            ))
        
        # Detecções por câmera
        detections_by_camera = self.repository.get_detections_by_camera(period)
        if detections_by_camera:
            avg_per_camera = sum(detections_by_camera.values()) / len(detections_by_camera)
            metrics.append(Metric(
                name="avg_detections_per_camera",
                value=avg_per_camera,
                period=period,
                metadata={"type": "average"}
            ))
        
        summary = {
            "period_start": period.start_date.isoformat(),
            "period_end": period.end_date.isoformat(),
            "total_metrics": len(metrics)
        }
        
        return Dashboard(metrics=metrics, summary=summary)