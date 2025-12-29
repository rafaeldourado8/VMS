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
    plate_confidence: Optional[float] = None
    image_path: Optional[str] = None

class DetectionRequest(BaseModel):
    camera_id: int
    image_base64: str

class DetectionResponse(BaseModel):
    detections: List[Detection]
    processing_time_ms: float
    task_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    queue_size: int
    processed_total: int
    avg_processing_time_ms: float
    gpu_available: bool
    active_workers: int = 0
    active_streams: int = 0

class WebhookData(BaseModel):
    """Modelo para dados de webhook LPR."""
    Plate: Optional[dict] = None
    Channel: Optional[int] = None
    DeviceName: Optional[str] = None

class CameraInfo(BaseModel):
    """Informações da câmera."""
    id: int
    name: str
    rtsp_url: Optional[str] = None
    active: bool = True
    type: str = "rtsp"  # rtsp, webhook, etc
