from dataclasses import dataclass
from .point import Point
from ..exceptions import InvalidBoundingBoxException


@dataclass(frozen=True)
class BoundingBox:
    """Value Object para bounding box de detecção"""
    
    x: float
    y: float
    width: float
    height: float
    
    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise InvalidBoundingBoxException("Largura e altura devem ser positivas")
    
    def center(self) -> Point:
        """Retorna o centro do bounding box"""
        return Point(
            x=self.x + self.width / 2,
            y=self.y + self.height / 2
        )
    
    def area(self) -> float:
        """Retorna a área do bounding box"""
        return self.width * self.height
