from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from ..core.interfaces import IStreamRepository
from ..models import StreamSession, StreamMetrics, ConnectionLog

logger = logging.getLogger(__name__)

class StreamRepository(IStreamRepository):
    """Repositório de streams (Single Responsibility)"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def save_session(self, session_data: Dict[str, Any]) -> int:
        """Salva sessão de stream"""
        try:
            session = StreamSession(
                camera_id=session_data['camera_id'],
                rtsp_url=session_data['rtsp_url'],
                quality=session_data.get('quality', 80),
                fps=session_data.get('fps', 30),
                resolution=session_data.get('resolution'),
                status='active'
            )
            
            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)
            
            logger.info(f"Sessão salva: {session.id}")
            return session.id
            
        except Exception as e:
            logger.error(f"Erro ao salvar sessão: {str(e)}")
            await self.db.rollback()
            raise
    
    async def update_session(self, session_id: int, data: Dict[str, Any]) -> bool:
        """Atualiza sessão"""
        try:
            session = await self.db.get(StreamSession, session_id)
            
            if not session:
                return False
            
            for key, value in data.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            
            await self.db.commit()
            logger.info(f"Sessão atualizada: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar sessão: {str(e)}")
            await self.db.rollback()
            return False
    
    async def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Obtém sessão"""
        try:
            session = await self.db.get(StreamSession, session_id)
            
            if not session:
                return None
            
            return {
                'id': session.id,
                'camera_id': session.camera_id,
                'rtsp_url': session.rtsp_url,
                'started_at': session.started_at,
                'ended_at': session.ended_at,
                'duration': session.duration,
                'total_frames': session.total_frames,
                'quality': session.quality,
                'fps': session.fps,
                'resolution': session.resolution,
                'status': session.status
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter sessão: {str(e)}")
            return None
    
    async def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Obtém sessões ativas"""
        try:
            from sqlalchemy import select
            
            stmt = select(StreamSession).where(StreamSession.status == 'active')
            result = await self.db.execute(stmt)
            sessions = result.scalars().all()
            
            return [
                {
                    'id': s.id,
                    'camera_id': s.camera_id,
                    'started_at': s.started_at,
                    'total_frames': s.total_frames
                }
                for s in sessions
            ]
            
        except Exception as e:
            logger.error(f"Erro ao obter sessões ativas: {str(e)}")
            return []
    
    async def save_metrics(self, metrics_data: Dict[str, Any]) -> int:
        """Salva métricas"""
        try:
            metrics = StreamMetrics(
                camera_id=metrics_data['camera_id'],
                fps_actual=metrics_data.get('fps_actual'),
                bitrate=metrics_data.get('bitrate'),
                frame_drops=metrics_data.get('frame_drops', 0),
                latency=metrics_data.get('latency'),
                bandwidth=metrics_data.get('bandwidth'),
                connected_clients=metrics_data.get('connected_clients', 0)
            )
            
            self.db.add(metrics)
            await self.db.commit()
            await self.db.refresh(metrics)
            
            return metrics.id
            
        except Exception as e:
            logger.error(f"Erro ao salvar métricas: {str(e)}")
            await self.db.rollback()
            raise
    
    async def save_connection_log(self, log_data: Dict[str, Any]) -> int:
        """Salva log de conexão"""
        try:
            log = ConnectionLog(
                camera_id=log_data['camera_id'],
                client_ip=log_data.get('client_ip'),
                user_agent=log_data.get('user_agent')
            )
            
            self.db.add(log)
            await self.db.commit()
            await self.db.refresh(log)
            
            return log.id
            
        except Exception as e:
            logger.error(f"Erro ao salvar log: {str(e)}")
            await self.db.rollback()
            raise