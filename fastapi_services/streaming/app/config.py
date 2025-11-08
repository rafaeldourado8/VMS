from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Configurações da aplicação (Single Responsibility)"""
    
    # Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Streaming
    DEFAULT_QUALITY: int = 80
    DEFAULT_FPS: int = 30
    MAX_STREAMS: int = 50
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/vms_streaming"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()