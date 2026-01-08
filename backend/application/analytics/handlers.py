from .queries import GetMetricsQuery, GetDashboardQuery, GetAggregatedMetricsQuery
from datetime import datetime, timedelta
from typing import Dict, Any, List

from ...domain.analytics.entities.metric import Metric, MetricType
from ...domain.analytics.repositories.metric_repository import MetricRepository

class GetMetricsHandler:
    """Handler para buscar métricas."""
    
    def __init__(self, metric_repository: MetricRepository):
        self._metric_repository = metric_repository
    
    def handle(self, query: GetMetricsQuery) -> List[Metric]:
        return self._metric_repository.get_metrics_by_type(
            query.metric_type,
            query.start_date,
            query.end_date
        )

class GetDashboardHandler:
    """Handler para dados do dashboard."""
    
    def __init__(self, metric_repository: MetricRepository):
        self._metric_repository = metric_repository
    
    def handle(self, query: GetDashboardQuery) -> Dict[str, Any]:
        end_date = query.end_date or datetime.now()
        start_date = query.start_date or (end_date - timedelta(days=7))
        
        # Métricas principais
        camera_metrics = self._metric_repository.get_aggregated_metrics(
            MetricType.CAMERA_STATUS, start_date, end_date, "avg"
        )
        
        detection_metrics = self._metric_repository.get_aggregated_metrics(
            MetricType.DETECTION_COUNT, start_date, end_date, "sum"
        )
        
        return {
            "cameras": camera_metrics,
            "detections": detection_metrics,
            "period": {"start": start_date, "end": end_date}
        }

class GetAggregatedMetricsHandler:
    """Handler para métricas agregadas."""
    
    def __init__(self, metric_repository: MetricRepository):
        self._metric_repository = metric_repository
    
    def handle(self, query: GetAggregatedMetricsQuery) -> Dict[str, Any]:
        return self._metric_repository.get_aggregated_metrics(
            query.metric_type,
            query.start_date,
            query.end_date,
            query.aggregation
        )