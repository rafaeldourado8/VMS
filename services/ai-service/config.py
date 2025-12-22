from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_host: str = "redis_cache"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 1
    
    workers: int = 4
    max_queue_size: int = 1000
    batch_size: int = 8
    confidence_threshold: float = 0.5
    
    yolo_model: str = "yolov8n.pt"
    lpr_model: str = "models/lpr_model.h5"
    vehicle_model: str = "models/vehicle_classifier.h5"
    
    enable_gpu: bool = False
    gpu_memory_fraction: float = 0.8
    
    log_level: str = "INFO"
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
