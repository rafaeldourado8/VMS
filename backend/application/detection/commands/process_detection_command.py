from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ProcessDetectionCommand:
    """Command para processar uma detecção"""
    
    camera_id: int
    plate: Optional[str]
    confidence: Optional[float]
    timestamp: datetime
    vehicle_type: str = "unknown"
    image_url: Optional[str] = None
    video_url: Optional[str] = None
