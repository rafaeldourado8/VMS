from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class UpdateROICommand:
    """Command para atualizar ROI de uma câmera"""
    
    camera_id: int
    polygon_points: List[Tuple[float, float]]
    enabled: bool = True
    name: str = "ROI"
