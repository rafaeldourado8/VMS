"""
Modelos de banco de dados para detecções de IA
Banco separado com cache Redis
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, LargeBinary, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional
import redis
import json
import hashlib

Base = declarative_base()

class DetectionZoneConfig(Base):
    """Configuração de zonas P1-P2"""
    __tablename__ = 'detection_zones'
    
    id = Column(Integer, primary_key=True)
    camera_id = Column(Integer, unique=True, nullable=False, index=True)
    p1_x = Column(Integer, nullable=False)
    p1_y = Column(Integer, nullable=False)
    p2_x = Column(Integer, nullable=False)
    p2_y = Column(Integer, nullable=False)
    distance_meters = Column(Float, nullable=False)
    speed_limit_kmh = Column(Float, nullable=False)
    fps = Column(Float, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VehicleDetection(Base):
    """Detecções de veículos"""
    __tablename__ = 'vehicle_detections'
    
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(String(32), unique=True, nullable=False, index=True)
    camera_id = Column(Integer, nullable=False, index=True)
    plate_text = Column(String(20), nullable=False, index=True)
    speed_kmh = Column(Float, nullable=False)
    speeding = Column(Boolean, nullable=False, index=True)
    speed_limit_kmh = Column(Float, nullable=False)
    timestamp_p1 = Column(DateTime, nullable=False, index=True)
    timestamp_p2 = Column(DateTime, nullable=False)
    frame_count = Column(Integer, nullable=False)
    plate_image = Column(LargeBinary, nullable=False)
    bbox_x = Column(Integer)
    bbox_y = Column(Integer)
    bbox_w = Column(Integer)
    bbox_h = Column(Integer)
    processed = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_camera_date', 'camera_id', 'created_at'),
        Index('idx_speeding_date', 'speeding', 'created_at'),
    )

class DetectionCache:
    """Cache Redis para evitar duplicatas"""
    
    def __init__(self, redis_url: str = 'redis://redis_cache:6379/3'):
        self.redis = redis.from_url(redis_url)
        self.ttl = 300  # 5 minutos
    
    def generate_key(self, camera_id: int, plate_text: str, timestamp: datetime) -> str:
        """Gera chave única para detecção"""
        data = f"{camera_id}_{plate_text}_{timestamp.strftime('%Y%m%d%H%M')}"
        return f"detection:{hashlib.md5(data.encode()).hexdigest()}"
    
    def is_duplicate(self, camera_id: int, plate_text: str, timestamp: datetime) -> bool:
        """Verifica se é duplicata"""
        key = self.generate_key(camera_id, plate_text, timestamp)
        return self.redis.exists(key) > 0
    
    def mark_detected(self, camera_id: int, plate_text: str, timestamp: datetime, vehicle_id: str):
        """Marca como detectado"""
        key = self.generate_key(camera_id, plate_text, timestamp)
        self.redis.setex(key, self.ttl, vehicle_id)
    
    def get_recent_detections(self, camera_id: int, limit: int = 10) -> list:
        """Obtém detecções recentes do cache"""
        pattern = f"detection:*"
        keys = self.redis.keys(pattern)
        
        detections = []
        for key in keys[:limit]:
            vehicle_id = self.redis.get(key)
            if vehicle_id:
                detections.append(vehicle_id.decode())
        
        return detections

class DetectionDatabase:
    """Gerenciador de banco de dados de detecções"""
    
    def __init__(self, db_url: str = 'postgresql://gtvision_user:your-strong-password-here@postgres_db/gtvision_db'):
        self.engine = create_engine(db_url, pool_size=10, max_overflow=20)
        # Não criar tabelas automaticamente - usar apenas se não existirem
        try:
            Base.metadata.create_all(self.engine, checkfirst=True)
        except Exception as e:
            # Ignorar erros de tabelas já existentes
            pass
        self.Session = sessionmaker(bind=self.engine)
        self.cache = DetectionCache()
    
    def save_detection(self, detection_data: dict) -> bool:
        """Salva detecção evitando duplicatas"""
        camera_id = detection_data['camera_id']
        plate_text = detection_data['plate_text']
        timestamp = detection_data['timestamp_p1']
        
        # Verifica duplicata no cache
        if self.cache.is_duplicate(camera_id, plate_text, timestamp):
            return False
        
        session = self.Session()
        try:
            detection = VehicleDetection(
                vehicle_id=detection_data['vehicle_id'],
                camera_id=camera_id,
                plate_text=plate_text,
                speed_kmh=detection_data['speed_kmh'],
                speeding=detection_data['speeding'],
                speed_limit_kmh=detection_data['speed_limit_kmh'],
                timestamp_p1=timestamp,
                timestamp_p2=detection_data['timestamp_p2'],
                frame_count=detection_data['frame_count'],
                plate_image=detection_data['plate_image'],
                bbox_x=detection_data['bbox'][0],
                bbox_y=detection_data['bbox'][1],
                bbox_w=detection_data['bbox'][2],
                bbox_h=detection_data['bbox'][3]
            )
            
            session.add(detection)
            session.commit()
            
            # Marca no cache
            self.cache.mark_detected(camera_id, plate_text, timestamp, detection_data['vehicle_id'])
            
            return True
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_speeding_violations(self, camera_id: Optional[int] = None, limit: int = 100) -> list:
        """Obtém infrações de velocidade"""
        session = self.Session()
        try:
            query = session.query(VehicleDetection).filter(VehicleDetection.speeding == True)
            
            if camera_id:
                query = query.filter(VehicleDetection.camera_id == camera_id)
            
            query = query.order_by(VehicleDetection.created_at.desc()).limit(limit)
            
            return query.all()
        finally:
            session.close()
    
    def configure_zone(self, zone_config: dict) -> bool:
        """Configura zona de detecção"""
        session = self.Session()
        try:
            zone = DetectionZoneConfig(
                camera_id=zone_config['camera_id'],
                p1_x=zone_config['p1'][0],
                p1_y=zone_config['p1'][1],
                p2_x=zone_config['p2'][0],
                p2_y=zone_config['p2'][1],
                distance_meters=zone_config['distance_meters'],
                speed_limit_kmh=zone_config['speed_limit_kmh'],
                fps=zone_config['fps']
            )
            
            session.merge(zone)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_zone_config(self, camera_id: int) -> Optional[dict]:
        """Obtém configuração de zona"""
        session = self.Session()
        try:
            zone = session.query(DetectionZoneConfig).filter(
                DetectionZoneConfig.camera_id == camera_id,
                DetectionZoneConfig.active == True
            ).first()
            
            if not zone:
                return None
            
            return {
                'camera_id': zone.camera_id,
                'p1': (zone.p1_x, zone.p1_y),
                'p2': (zone.p2_x, zone.p2_y),
                'distance_meters': zone.distance_meters,
                'speed_limit_kmh': zone.speed_limit_kmh,
                'fps': zone.fps
            }
        finally:
            session.close()