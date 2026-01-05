from dataclasses import dataclass
from ..value_objects.point import Point


@dataclass
class VirtualLine:
    """Entidade de domínio VirtualLine (P1 ou P2)"""
    
    p1: Point
    p2: Point
    name: str
    
    def intersects(self, point_a: Point, point_b: Point) -> bool:
        """Verifica se o segmento point_a -> point_b cruza a linha"""
        def ccw(A: Point, B: Point, C: Point) -> bool:
            return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)
        
        return (ccw(self.p1, point_a, point_b) != ccw(self.p2, point_a, point_b) and
                ccw(self.p1, self.p2, point_a) != ccw(self.p1, self.p2, point_b))
    
    def distance_to(self, point: Point) -> float:
        """Calcula distância perpendicular do ponto à linha"""
        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y
        x0, y0 = point.x, point.y
        
        num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        den = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5
        
        return num / den if den > 0 else 0
