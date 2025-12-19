from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class DeteccaoDTO:
    """DTO para leitura/exposição de detecções."""
    id: int
    camera_id: int
    camera_name: str
    plate: Optional[str]
    confidence: Optional[float]
    timestamp: datetime
    vehicle_type: str
    image_url: Optional[str]
    video_url: Optional[str]

    @classmethod
    def from_model(cls, instance):
        return cls(
            id=instance.id,
            camera_id=instance.camera.id,
            camera_name=instance.camera.name,
            plate=instance.plate,
            confidence=instance.confidence,
            timestamp=instance.timestamp,
            vehicle_type=instance.vehicle_type,
            image_url=instance.image_url,
            video_url=instance.video_url
        )

@dataclass(frozen=True)
class IngestDeteccaoDTO:
    """DTO para dados brutos de ingestão vindos da IA."""
    camera_id: int
    timestamp: datetime
    plate: Optional[str] = None
    confidence: Optional[float] = None
    vehicle_type: str = "unknown"
    image_url: Optional[str] = None
    video_url: Optional[str] = None