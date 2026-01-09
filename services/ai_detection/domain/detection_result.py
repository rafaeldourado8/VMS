from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DetectionResult(BaseModel):
    camera_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    provider: str
    detections: List[Dict[str, Any]]
    confidence_avg: float
    frame_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
