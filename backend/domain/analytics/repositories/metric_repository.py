from ..entities.metric import Metric, MetricType
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any

class MetricRepository(ABC):
    """Interface para repositório de métricas."""
    
    @abstractmethod
    def save(self, metric: Metric) -> Metric:
        """Salva uma métrica."""
        pass
    
    @abstractmethod
    def get_metrics_by_type(
        self, 
        metric_type: MetricType,
        start_date: datetime,
        end_date: datetime
    ) -> List[Metric]:
        """Busca métricas por tipo e período."""
        pass
    
    @abstractmethod
    def get_aggregated_metrics(
        self,
        metric_type: MetricType,
        start_date: datetime,
        end_date: datetime,
        aggregation: str = "avg"
    ) -> Dict[str, Any]:
        """Retorna métricas agregadas."""
        pass