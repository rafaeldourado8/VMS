# fastapi_services/streaming/app/services/stream_manager.py
from typing import Dict, Optional, List
import asyncio
import logging
from datetime import datetime

from ..core.interfaces import IStreamReader, IFrameEncoder
from ..schemas import StreamConfig, StreamInfo
from .pipeline import ProcessingPipeline
from .stream_reader import RTSPStreamReader
from .frame_encoder import MJPEGEncoder
from .frame_processors import (
    ResizeProcessor,
    QualityProcessor,
    WatermarkProcessor,
    TimestampProcessor
)

logger = logging.getLogger(__name__)

class StreamSession:
    """Representa uma sessão de streaming (Single Responsibility)"""
    
    def __init__(
        self,
        camera_id: str,
        reader: IStreamReader,
        encoder: IFrameEncoder,
        pipeline: ProcessingPipeline
    ):
        self.camera_id = camera_id
        self.reader = reader
        self.encoder = encoder
        self.pipeline = pipeline
        
        self.started_at = datetime.now()
        self.frame_count = 0
        self.error_count = 0
        self.is_active = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self) -> bool:
        """Inicia sessão"""
        if self.is_active:
            return True
        
        success = await self.reader.connect()
        if success:
            self.is_active = True
            logger.info(f"Sessão iniciada: {self.camera_id}")
        
        return success
    
    async def stop(self) -> None:
        """Para sessão"""
        if not self.is_active:
            return
        
        self.is_active = False
        await self.reader.disconnect()
        
        if self._task:
            self._task.cancel()
        
        logger.info(f"Sessão parada: {self.camera_id}")
    
    async def read_and_process_frame(self) -> Optional[bytes]:
        """Lê e processa um frame"""
        if not self.is_active:
            return None
        
        try:
            # Lê frame
            frame = await self.reader.read_frame()
            if frame is None:
                self.error_count += 1
                return None
            
            # Processa frame
            processed_frame = await self.pipeline.process(frame)
            
            # Codifica frame
            encoded_frame = await self.encoder.encode(processed_frame)
            
            self.frame_count += 1
            return encoded_frame
            
        except Exception as e:
            logger.error(f"Erro ao processar frame: {str(e)}")
            self.error_count += 1
            return None
    
    def get_info(self) -> StreamInfo:
        """Retorna informações da sessão"""
        duration = (datetime.now() - self.started_at).total_seconds()
        fps = self.frame_count / duration if duration > 0 else 0
        
        return StreamInfo(
            camera_id=self.camera_id,
            is_active=self.is_active,
            started_at=self.started_at,
            frame_count=self.frame_count,
            error_count=self.error_count,
            fps=fps,
            properties=self.reader.get_properties()
        )


class StreamManager:
    """Gerenciador de streams (Facade Pattern)"""
    
    def __init__(self):
        self._sessions: Dict[str, StreamSession] = {}
        self._lock = asyncio.Lock()
    
    async def create_stream(self, camera_id: str, config: StreamConfig) -> bool:
        """Cria um novo stream"""
        async with self._lock:
            if camera_id in self._sessions:
                logger.warning(f"Stream já existe: {camera_id}")
                return False
            
            try:
                # Cria componentes (Dependency Injection)
                reader = self._create_reader(config)
                encoder = self._create_encoder(config)
                pipeline = self._create_pipeline(config)
                
                # Cria sessão
                session = StreamSession(camera_id, reader, encoder, pipeline)
                
                # Inicia sessão
                success = await session.start()
                
                if success:
                    self._sessions[camera_id] = session
                    logger.info(f"Stream criado: {camera_id}")
                
                return success
                
            except Exception as e:
                logger.error(f"Erro ao criar stream: {str(e)}")
                return False
    
    async def stop_stream(self, camera_id: str) -> bool:
        """Para um stream"""
        async with self._lock:
            session = self._sessions.get(camera_id)
            
            if not session:
                logger.warning(f"Stream não encontrado: {camera_id}")
                return False
            
            await session.stop()
            del self._sessions[camera_id]
            
            logger.info(f"Stream parado: {camera_id}")
            return True
    
    async def stop_all_streams(self) -> None:
        """Para todos os streams"""
        async with self._lock:
            for session in self._sessions.values():
                await session.stop()
            
            self._sessions.clear()
            logger.info("Todos os streams parados")
    
    async def get_frame(self, camera_id: str) -> Optional[bytes]:
        """Obtém frame de um stream"""
        session = self._sessions.get(camera_id)
        
        if not session:
            return None
        
        return await session.read_and_process_frame()
    
    def get_stream_info(self, camera_id: str) -> Optional[StreamInfo]:
        """Obtém informações de um stream"""
        session = self._sessions.get(camera_id)
        return session.get_info() if session else None
    
    def list_streams(self) -> List[StreamInfo]:
        """Lista todos os streams"""
        return [session.get_info() for session in self._sessions.values()]
    
    def stream_exists(self, camera_id: str) -> bool:
        """Verifica se stream existe"""
        return camera_id in self._sessions
    
    # Factory Methods (Factory Pattern)
    def _create_reader(self, config: StreamConfig) -> IStreamReader:
        """Cria leitor de stream"""
        return RTSPStreamReader(
            stream_url=config.rtsp_url,
            reconnect_attempts=3,
            reconnect_delay=5
        )
    
    def _create_encoder(self, config: StreamConfig) -> IFrameEncoder:
        """Cria encoder de frame"""
        return MJPEGEncoder(quality=config.quality)
    
    def _create_pipeline(self, config: StreamConfig) -> ProcessingPipeline:
        """Cria pipeline de processamento"""
        pipeline = ProcessingPipeline()
        
        # Adiciona processadores baseado na configuração
        if config.resize:
            pipeline.add_processor(ResizeProcessor(max_width=1280))
        
        if config.quality < 100:
            pipeline.add_processor(QualityProcessor(quality=config.quality))
        
        if config.watermark:
            pipeline.add_processor(WatermarkProcessor(text="VMS"))
        
        if config.timestamp:
            pipeline.add_processor(TimestampProcessor())
        
        return pipeline