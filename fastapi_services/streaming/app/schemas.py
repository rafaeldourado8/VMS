from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class StreamProtocol(str, Enum):
    """Protocolos de streaming suportados."""
    RTSP = "rtsp"
    HTTP = "http"
    HTTPS = "https"
    FILE = "file"


class StreamStatus(str, Enum):
    """Status possíveis de um stream."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    CONNECTING = "connecting"


class StreamCreate(BaseModel):
    """Schema para criação de um novo stream."""
    
    stream_url: str = Field(
        ...,
        description="URL do stream (RTSP, HTTP, ou caminho de arquivo)",
        min_length=1
    )
    camera_id: int = Field(
        ...,
        description="ID da câmera associada ao stream",
        gt=0
    )
    protocol: StreamProtocol = Field(
        default=StreamProtocol.RTSP,
        description="Protocolo do stream"
    )
    
    @field_validator('stream_url')
    @classmethod
    def validate_stream_url(cls, v: str) -> str:
        """Valida a URL do stream."""
        if not v or not v.strip():
            raise ValueError("URL do stream não pode estar vazia")
        
        # Validação básica de protocolo
        valid_prefixes = ('rtsp://', 'http://', 'https://', 'file://', '/')
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(
                f"URL deve começar com um dos protocolos: {', '.join(valid_prefixes)}"
            )
        
        return v.strip()
    
    @field_validator('camera_id')
    @classmethod
    def validate_camera_id(cls, v: int) -> int:
        """Valida o ID da câmera."""
        if v <= 0:
            raise ValueError("ID da câmera deve ser maior que zero")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "stream_url": "rtsp://admin:password@192.168.1.100:554/stream1",
                "camera_id": 1,
                "protocol": "rtsp"
            }
        }


class StreamResponse(BaseModel):
    """Schema para resposta de informações do stream."""
    
    stream_id: str = Field(..., description="ID único do stream")
    camera_id: int = Field(..., description="ID da câmera")
    stream_url: str = Field(..., description="URL do stream")
    status: StreamStatus = Field(..., description="Status atual do stream")
    protocol: StreamProtocol = Field(..., description="Protocolo do stream")
    fps: Optional[float] = Field(None, description="FPS atual do stream")
    resolution: Optional[str] = Field(None, description="Resolução do stream (WxH)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stream_id": "stream_1_1234567890",
                "camera_id": 1,
                "stream_url": "rtsp://admin:password@192.168.1.100:554/stream1",
                "status": "active",
                "protocol": "rtsp",
                "fps": 30.0,
                "resolution": "1920x1080"
            }
        }


class StreamUpdate(BaseModel):
    """Schema para atualização de um stream."""
    
    stream_url: Optional[str] = Field(
        None,
        description="Nova URL do stream",
        min_length=1
    )
    protocol: Optional[StreamProtocol] = Field(
        None,
        description="Novo protocolo do stream"
    )
    
    @field_validator('stream_url')
    @classmethod
    def validate_stream_url(cls, v: Optional[str]) -> Optional[str]:
        """Valida a URL do stream se fornecida."""
        if v is None:
            return v
            
        if not v.strip():
            raise ValueError("URL do stream não pode estar vazia")
        
        valid_prefixes = ('rtsp://', 'http://', 'https://', 'file://', '/')
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(
                f"URL deve começar com um dos protocolos: {', '.join(valid_prefixes)}"
            )
        
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "stream_url": "rtsp://admin:newpassword@192.168.1.100:554/stream1",
                "protocol": "rtsp"
            }
        }


class HealthResponse(BaseModel):
    """Schema para resposta de health check."""
    
    status: str = Field(..., description="Status do serviço")
    active_streams: int = Field(..., description="Número de streams ativos")
    version: str = Field(..., description="Versão do serviço")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "active_streams": 5,
                "version": "1.0.0"
            }
        }


class ErrorResponse(BaseModel):
    """Schema para respostas de erro."""
    
    detail: str = Field(..., description="Descrição do erro")
    error_code: Optional[str] = Field(None, description="Código do erro")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Stream não encontrado",
                "error_code": "STREAM_NOT_FOUND"
            }
        }


class FrameMetadata(BaseModel):
    """Schema para metadados de um frame."""
    
    timestamp: float = Field(..., description="Timestamp do frame")
    frame_number: int = Field(..., description="Número do frame")
    fps: float = Field(..., description="FPS atual")
    resolution: str = Field(..., description="Resolução do frame")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": 1234567890.123,
                "frame_number": 1500,
                "fps": 30.0,
                "resolution": "1920x1080"
            }
        }

