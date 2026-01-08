from datetime import datetime
from typing import Dict, Any

from ...domain.analytics.entities.metric import Metric, MetricType

class MetricMapper:
    """Mapper para conversão entre domínio e dados."""
    
    @staticmethod
    def to_domain(data: Dict[str, Any]) -> Metric:
        """Converte dados para entidade de domínio."""
        return Metric(
            id=data.get("id"),
            type=MetricType(data["type"]),
            value=float(data["value"]),
            metadata=data.get("metadata", {}),
            timestamp=data["timestamp"]
        )
    
    @staticmethod
    def to_dict(metric: Metric) -> Dict[str, Any]:
        """Converte entidade para dicionário."""
        return {
            "id": metric.id,
            "type": metric.type.value,
            "value": metric.value,
            "metadata": metric.metadata,
            "timestamp": metric.timestamp
        }