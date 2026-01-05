from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateCameraCommand:
    """Command para criar uma câmera"""
    
    owner_id: int
    name: str
    stream_url: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    thumbnail_url: Optional[str] = None
