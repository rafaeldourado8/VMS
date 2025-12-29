from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Redis Configuration
    redis_host: str = "redis_cache"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 1
    
    # Worker Configuration
    workers: int = 4
    max_queue_size: int = 1000
    batch_size: int = 8
    
    # Detection Thresholds
    confidence_threshold: float = 0.5
    motion_threshold: int = 500  # Minimum contour area for motion detection
    motion_min_change: float = 0.02  # Minimum percentage of frame change
    
    # Model Paths
    yolo_model: str = "yolov8n.pt"
    ocr_model: str = "cct-xs-v1-global-model"  # fast-plate-ocr model
    
    # GPU Configuration
    enable_gpu: bool = False
    gpu_memory_fraction: float = 0.8
    
    # Directory Paths
    captures_dir: str = "/app/captures"
    pending_training_dir: str = "/app/pending_training"
    received_webhooks_dir: str = "/app/received_webhooks"
    models_dir: str = "/app/models"
    logs_dir: str = "/app/logs"
    
    # Logging and Monitoring
    log_level: str = "INFO"
    metrics_port: int = 9090
    
    # RTSP Stream Configuration
    rtsp_enabled: bool = True
    rtsp_reconnect_delay: int = 10  # seconds
    rtsp_frame_skip: int = 5  # Process every N frames for optimization
    
    # Backend API Configuration
    backend_url: str = "http://gt-vision-backend:8000"
    admin_api_key: Optional[str] = None
    
    # Webhook Configuration
    webhook_port: int = 5000
    webhook_save_json: bool = True
    
    # Detection Classes (COCO dataset)
    vehicle_classes: list = [2, 3, 5, 7]  # car, motorcycle, bus, truck
    plate_classes: list = [2, 7]  # Classes where plates are commonly detected
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
