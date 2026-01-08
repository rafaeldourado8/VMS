from ..exceptions import InvalidCoordinatesException
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class GeoCoordinates:
    """Value Object para coordenadas geográficas"""
    
    latitude: Optional[float]
    longitude: Optional[float]
    
    def __post_init__(self):
        if self.latitude is not None:
            if not -90 <= self.latitude <= 90:
                raise InvalidCoordinatesException(
                    f"Latitude deve estar entre -90 e 90: {self.latitude}"
                )
        
        if self.longitude is not None:
            if not -180 <= self.longitude <= 180:
                raise InvalidCoordinatesException(
                    f"Longitude deve estar entre -180 e 180: {self.longitude}"
                )
    
    def is_valid(self) -> bool:
        return self.latitude is not None and self.longitude is not None
