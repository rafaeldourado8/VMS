from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class Detection(BaseModel):
    """Schema para uma detecção individual"""
    bbox: List[int] = Field(..., description="Bounding box [x1, y1, x2, y2]")
    confidence: float = Field(..., ge=0, le=1, description="Confiança da detecção")
    class_name: str = Field(..., description="Nome da classe detectada")
    class_id: int = Field(..., description="ID da classe")
    
    @validator('bbox')
    def validate_bbox(cls, v):
        if len(v) != 4:
            raise ValueError('Bbox deve ter 4 valores [x1, y1, x2, y2]')
        return v

class DetectionConfig(BaseModel):
    """Configuração para detecção"""
    rtsp_url: str = Field(..., description="URL RTSP da câmera")
    confidence: float = Field(0.5, ge=0, le=1, description="Confiança mínima")
    classes: Optional[List[str]] = Field(None, description="Classes específicas para detectar")
    fps: Optional[int] = Field(10, ge=1, le=30, description="FPS de processamento")
    draw_boxes: bool = Field(True, description="Desenhar caixas nas detecções")
    include_frame: bool = Field(False, description="Incluir frame na resposta")
    alert_enabled: bool = Field(False, description="Habilitar alertas")

class DetectionResult(BaseModel):
    """Resultado de detecção"""
    camera_id: str
    timestamp: datetime
    detections: List[Detection]
    frame_base64: Optional[str] = None
    total_detections: int
    processing_time: Optional[float] = None

class ModelInfo(BaseModel):
    """Informações sobre um modelo"""
    name: str
    version: str
    type: str  # yolov8, yolov5, etc
    classes: List[str]
    input_size: List[int]
    device: str
    loaded: bool

class AlertConfig(BaseModel):
    """Configuração de alertas"""
    enabled: bool = True
    classes: Optional[List[str]] = None
    min_confidence: float = 0.7
    max_objects: Optional[int] = None
    cooldown: int = 60  # segundos entre alertas

class AlertResponse(BaseModel):
    """Resposta de alerta"""
    alert_id: str
    camera_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    detections: List[Detection]