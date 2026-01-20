import os
from dataclasses import dataclass

@dataclass
class Settings:
    # MediaMTX
    MEDIAMTX_URL: str = os.getenv("MEDIAMTX_URL", "http://mediamtx:9997")
    MEDIAMTX_WEBRTC_URL: str = os.getenv("MEDIAMTX_WEBRTC_URL", "http://mediamtx:8889")
    USE_WEBRTC: bool = os.getenv("USE_WEBRTC", "true").lower() == "true"
    
    # Frame Processing
    AI_FPS: int = int(os.getenv("AI_FPS", "3"))
    RTSP_TIMEOUT_MS: int = int(os.getenv("RTSP_TIMEOUT_MS", "5000"))
    RTSP_RETRY_DELAY: int = int(os.getenv("RTSP_RETRY_DELAY", "5"))
    
    # Motion Detection
    MOTION_THRESHOLD: float = float(os.getenv("MOTION_THRESHOLD", "0.03"))
    MOG2_VAR_THRESHOLD: int = int(os.getenv("MOG2_VAR_THRESHOLD", "16"))
    MOG2_HISTORY: int = int(os.getenv("MOG2_HISTORY", "500"))
    
    # Vehicle Detection
    VEHICLE_CONFIDENCE: float = float(os.getenv("VEHICLE_CONFIDENCE", "0.5"))
    VEHICLE_MODEL: str = os.getenv("VEHICLE_MODEL", "models/vehicle_yolov8n.pt")
    
    # Tracking
    TRACKER_IOU_THRESHOLD: float = float(os.getenv("TRACKER_IOU_THRESHOLD", "0.3"))
    TRACKER_TIMEOUT: int = int(os.getenv("TRACKER_TIMEOUT", "5"))
    
    # Quality Scoring
    QUALITY_WEIGHT_BLUR: float = float(os.getenv("QUALITY_WEIGHT_BLUR", "0.35"))
    QUALITY_WEIGHT_ANGLE: float = float(os.getenv("QUALITY_WEIGHT_ANGLE", "0.30"))
    QUALITY_WEIGHT_CONTRAST: float = float(os.getenv("QUALITY_WEIGHT_CONTRAST", "0.20"))
    QUALITY_WEIGHT_SIZE: float = float(os.getenv("QUALITY_WEIGHT_SIZE", "0.15"))
    MIN_QUALITY_SCORE: float = float(os.getenv("MIN_QUALITY_SCORE", "50"))
    
    # Plate Detection (FINE-TUNED MODEL)
    PLATE_CONFIDENCE: float = float(os.getenv("PLATE_CONFIDENCE", "0.6"))
    PLATE_MODEL: str = os.getenv("PLATE_MODEL", "models/plate_yolov8n.pt")
    
    # OCR
    OCR_MODEL: str = os.getenv("OCR_MODEL", "cct-xs-v1-global-model")
    
    # Consensus
    MIN_READINGS: int = int(os.getenv("MIN_READINGS", "3"))
    MAX_READINGS: int = int(os.getenv("MAX_READINGS", "5"))
    CONSENSUS_THRESHOLD: float = float(os.getenv("CONSENSUS_THRESHOLD", "0.6"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.8"))
    MIN_CONFIDENCE: float = float(os.getenv("MIN_CONFIDENCE", "0.75"))
    
    # Deduplication
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    DEDUP_TTL: int = int(os.getenv("DEDUP_TTL", "300"))
    
    # Backend
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://backend:8000")
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "rabbitmq")
    RABBITMQ_PORT: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER: str = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASS: str = os.getenv("RABBITMQ_PASS", "guest")
    
    # API
    API_PORT: int = int(os.getenv("API_PORT", "5000"))

settings = Settings()
