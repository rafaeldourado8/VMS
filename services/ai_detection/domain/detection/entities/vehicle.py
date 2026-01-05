from dataclasses import dataclass, field
from typing import Optional, List
from ..value_objects.bounding_box import BoundingBox
from ..value_objects.point import Point


@dataclass
class Vehicle:
    """Entidade de domínio Vehicle"""
    
    track_id: int
    bbox: BoundingBox
    confidence: float
    vehicle_type: str = "unknown"
    plate: Optional[str] = None
    plate_confidence: Optional[float] = None
    positions: List[Point] = field(default_factory=list)
    crossed_p1: bool = False
    crossed_p2: bool = False
    
    def update_position(self, bbox: BoundingBox) -> None:
        """Atualiza posição do veículo"""
        self.bbox = bbox
        self.positions.append(bbox.center())
    
    def mark_crossed_p1(self) -> None:
        """Marca que cruzou linha P1"""
        self.crossed_p1 = True
    
    def mark_crossed_p2(self) -> None:
        """Marca que cruzou linha P2"""
        self.crossed_p2 = True
    
    def set_plate(self, plate: str, confidence: float) -> None:
        """Define placa detectada"""
        self.plate = plate
        self.plate_confidence = confidence
    
    def has_plate(self) -> bool:
        """Verifica se tem placa detectada"""
        return self.plate is not None
    
    def is_ready_for_trigger(self) -> bool:
        """Verifica se está pronto para trigger (cruzou P1 mas não P2)"""
        return self.crossed_p1 and not self.crossed_p2
