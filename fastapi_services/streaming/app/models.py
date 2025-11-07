from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class StreamSession(Base):
    """Modelo para sessões de streaming"""
    __tablename__ = "stream_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, index=True, nullable=False)
    rtsp_url = Column(String, nullable=False)
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)
    total_frames = Column(Integer, default=0)
    quality = Column(Integer, default=80)
    fps = Column(Integer, default=30)
    resolution = Column(JSON, nullable=True)
    status = Column(String, default="active")
    error_message = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<StreamSession(camera_id={self.camera_id}, status={self.status})>"

class StreamMetrics(Base):
    """Modelo para métricas de streaming"""
    __tablename__ = "stream_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    fps_actual = Column(Float)
    bitrate = Column(Float)
    frame_drops = Column(Integer, default=0)
    latency = Column(Float)
    bandwidth = Column(Float)
    connected_clients = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<StreamMetrics(camera_id={self.camera_id}, fps={self.fps_actual})>"

class ConnectionLog(Base):
    """Modelo para log de conexões"""
    __tablename__ = "connection_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, index=True, nullable=False)
    client_ip = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    connected_at = Column(DateTime, default=func.now())
    disconnected_at = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)
    bytes_sent = Column(Integer, default=0)
    frames_sent = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<ConnectionLog(camera_id={self.camera_id}, client_ip={self.client_ip})>"