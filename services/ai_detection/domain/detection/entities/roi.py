from dataclasses import dataclass
from ..value_objects.polygon import Polygon
from ..value_objects.point import Point


@dataclass
class ROI:
    """Entidade de domínio ROI (Region of Interest)"""
    
    camera_id: int
    polygon: Polygon
    enabled: bool = True
    name: str = "ROI"
    
    def enable(self) -> None:
        """Habilita o ROI"""
        self.enabled = True
    
    def disable(self) -> None:
        """Desabilita o ROI"""
        self.enabled = False
    
    def contains_point(self, point: Point) -> bool:
        """Verifica se um ponto está dentro do ROI"""
        if not self.enabled:
            return True  # Se desabilitado, aceita tudo
        return self.polygon.contains_point(point)
    
    def is_enabled(self) -> bool:
        """Verifica se o ROI está habilitado"""
        return self.enabled
