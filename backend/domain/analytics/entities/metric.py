from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional

class MetricType(Enum):
    CAMERA_STATUS = "camera_status"
    DETECTION_COUNT = "detection_count"
    SYSTEM_PERFORMANCE = "system_performance"
    USER_ACTIVITY = "user_activity"

@dataclass(frozen=True)
class Metric:
    """Entidade que representa uma métrica do sistema."""
    
    id: Optional[str]
    type: MetricType
    value: float
    metadata: Dict[str, Any]
    timestamp: datetime
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Valor da métrica não pode ser negativo")
        
        if not isinstance(self.metadata, dict):
            raise ValueError("Metadata deve ser um dicionário")