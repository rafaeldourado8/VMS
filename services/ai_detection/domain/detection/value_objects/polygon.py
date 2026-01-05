from dataclasses import dataclass
from typing import List
from .point import Point
from ..exceptions import InvalidPolygonException


@dataclass(frozen=True)
class Polygon:
    """Value Object para polígono (ROI)"""
    
    points: tuple[Point, ...]
    
    def __post_init__(self):
        if len(self.points) < 3:
            raise InvalidPolygonException("Polígono deve ter no mínimo 3 pontos")
    
    def contains_point(self, point: Point) -> bool:
        """Verifica se um ponto está dentro do polígono (ray casting)"""
        n = len(self.points)
        inside = False
        
        p1 = self.points[0]
        for i in range(1, n + 1):
            p2 = self.points[i % n]
            if point.y > min(p1.y, p2.y):
                if point.y <= max(p1.y, p2.y):
                    if point.x <= max(p1.x, p2.x):
                        if p1.y != p2.y:
                            xinters = (point.y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x
                        if p1.x == p2.x or point.x <= xinters:
                            inside = not inside
            p1 = p2
        
        return inside
