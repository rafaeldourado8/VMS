from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class VehicleDistributionDTO:
    """DTO para distribuição de tipos de veículos."""
    type: str
    count: int
    percentage: float

@dataclass(frozen=True)
class DetectionPeriodDTO:
    """DTO para contagem de detecções por período temporal."""
    date: str
    count: int