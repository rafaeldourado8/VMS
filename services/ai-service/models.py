from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class BoundingBox(BaseModel):
    x: int
    y: int
    w: int
    h: int

class Detection(BaseModel):
    camera_id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    object_type: str
    confidence: float
    bbox: BoundingBox
    plate_number: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_confidence: Optional[float] = None

class DetectionRequest(BaseModel):
    camera_id: int
    image_base64: str

class DetectionResponse(BaseModel):
    detections: List[Detection]
    processing_time_ms: float

class HealthResponse(BaseModel):
    status: str
    queue_size: int
    processed_total: int
    avg_processing_time_ms: float
    gpu_available: bool
