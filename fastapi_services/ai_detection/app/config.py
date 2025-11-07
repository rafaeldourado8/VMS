from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Modelo
    DEFAULT_MODEL: str = "yolov8n"
    MODELS_DIR: str = "models"
    
    # Detecção
    DEFAULT_CONFIDENCE: float = 0.5
    DEFAULT_FPS: int = 10
    MAX_DETECTIONS: int = 100
    
    # GPU
    USE_GPU: bool = True
    GPU_MEMORY_FRACTION: float = 0.8
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1
    
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/vms_ai"
    
    # Alertas
    ALERT_COOLDOWN: int = 60  # segundos
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()