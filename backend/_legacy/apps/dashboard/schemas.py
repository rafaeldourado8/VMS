from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass(frozen=True)
class DashboardStatsDTO:
    """Objeto de transferência para métricas globais do sistema."""
    total_cameras: int
    cameras_online: int
    cameras_offline: int
    total_detections_24h: int
    detections_by_type: Dict[str, int]
    recent_activity: List[Dict[str, Any]]