from dataclasses import dataclass
from ..exceptions import InvalidPointException


@dataclass(frozen=True)
class Point:
    """Value Object para ponto 2D"""
    
    x: float
    y: float
    
    def __post_init__(self):
        if self.x < 0 or self.y < 0:
            raise InvalidPointException(f"Coordenadas devem ser positivas: ({self.x}, {self.y})")
    
    def distance_to(self, other: 'Point') -> float:
        """Calcula distância euclidiana para outro ponto"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
