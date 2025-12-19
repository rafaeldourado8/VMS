from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass(frozen=True)
class CameraDTO:
    """Objeto de transferência de dados para Câmaras."""
    name: str
    stream_url: str
    owner_id: int
    location: Optional[str] = None
    status: str = "online"
    thumbnail_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    detection_settings: Dict[str, Any] = field(default_factory=dict)
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_model(cls, camera):
        """Converte uma instância do Model Camera para DTO."""
        return cls(
            id=camera.id,
            owner_id=camera.owner.id,
            name=camera.name,
            location=camera.location,
            status=camera.status,
            stream_url=camera.stream_url,
            thumbnail_url=camera.thumbnail_url,
            latitude=camera.latitude,
            longitude=camera.longitude,
            detection_settings=camera.detection_settings,
            created_at=camera.created_at
        )