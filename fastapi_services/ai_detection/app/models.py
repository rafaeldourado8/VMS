from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class DetectionSession(Base):
    """Modelo para sessões de detecção"""
    __tablename__ = "detection_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, index=True, nullable=False)
    model_name = Column(String, nullable=False)
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)
    total_frames_processed = Column(Integer, default=0)
    total_detections = Column(Integer, default=0)
    confidence_threshold = Column(Float, default=0.5)
    classes_filter = Column(JSON, nullable=True)
    status = Column(String, default="active")  # active, stopped, error
    
    # Relacionamento com detecções
    detections = relationship("DetectionRecord", back_populates="session")
    
    def __repr__(self):
        return f"<DetectionSession(camera_id={self.camera_id}, model={self.model_name})>"

class DetectionRecord(Base):
    """Modelo para registros de detecção"""
    __tablename__ = "detection_records"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("detection_sessions.id"), nullable=False)
    camera_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=func.now(), index=True)
    frame_number = Column(Integer)
    detections = Column(JSON)  # Lista de detecções
    total_objects = Column(Integer, default=0)
    processing_time = Column(Float)  # Tempo de processamento em ms
    
    # Relacionamento com sessão
    session = relationship("DetectionSession", back_populates="detections")
    
    def __repr__(self):
        return f"<DetectionRecord(camera_id={self.camera_id}, objects={self.total_objects})>"

class Alert(Base):
    """Modelo para alertas"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, index=True, nullable=False)
    alert_type = Column(String, nullable=False)  # object_detected, threshold_exceeded, etc
    severity = Column(String, default="medium")  # low, medium, high, critical
    message = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now(), index=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Alert(camera_id={self.camera_id}, type={self.alert_type}, severity={self.severity})>"

class ModelMetrics(Base):
    """Modelo para métricas de modelos de IA"""
    __tablename__ = "model_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    avg_inference_time = Column(Float)  # Tempo médio de inferência em ms
    fps = Column(Float)  # FPS de processamento
    accuracy = Column(Float, nullable=True)
    total_detections = Column(Integer, default=0)
    memory_usage = Column(Float)  # Uso de memória em MB
    gpu_usage = Column(Float, nullable=True)  # Uso de GPU em %
    
    def __repr__(self):
        return f"<ModelMetrics(model={self.model_name}, fps={self.fps})>"