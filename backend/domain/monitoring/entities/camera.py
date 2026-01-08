from ..value_objects.geo_coordinates import GeoCoordinates
from ..value_objects.location import Location
from ..value_objects.stream_url import StreamUrl
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

class CameraStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"

@dataclass
class Camera:
    """Entidade de domínio Camera"""
    
    id: Optional[int]
    owner_id: int
    name: str
    stream_url: StreamUrl
    status: CameraStatus = CameraStatus.ONLINE
    location: Location = field(default_factory=lambda: Location(None))
    coordinates: GeoCoordinates = field(default_factory=lambda: GeoCoordinates(None, None))
    thumbnail_url: Optional[str] = None
    recording_enabled: bool = True
    recording_retention_days: int = 30
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def activate(self) -> None:
        """Ativa a câmera"""
        self.status = CameraStatus.ONLINE
    
    def deactivate(self) -> None:
        """Desativa a câmera"""
        self.status = CameraStatus.OFFLINE
    
    def is_online(self) -> bool:
        """Verifica se a câmera está online"""
        return self.status == CameraStatus.ONLINE
    
    def update_location(self, location: Location, coordinates: GeoCoordinates) -> None:
        """Atualiza localização da câmera"""
        self.location = location
        self.coordinates = coordinates
    
    def enable_recording(self, retention_days: int = 30) -> None:
        """Habilita gravação"""
        if retention_days not in [7, 15, 30]:
            retention_days = 30
        self.recording_enabled = True
        self.recording_retention_days = retention_days
    
    def disable_recording(self) -> None:
        """Desabilita gravação"""
        self.recording_enabled = False
