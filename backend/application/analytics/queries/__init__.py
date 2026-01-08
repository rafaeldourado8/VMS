from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ...domain.analytics.entities.metric import MetricType


@dataclass(frozen=True)
class GetMetricsQuery:
    """Query para buscar métricas por tipo e período."""
    
    metric_type: MetricType
    start_date: datetime
    end_date: datetime


@dataclass(frozen=True)
class GetDashboardQuery:
    """Query para buscar dados do dashboard."""
    
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass(frozen=True)
class GetAggregatedMetricsQuery:
    """Query para métricas agregadas."""
    
    metric_type: MetricType
    start_date: datetime
    end_date: datetime
    aggregation: str = "avg"