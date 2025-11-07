# fastapi_services/streaming/app/services/stream_reader.py
import cv2
import numpy as np
from typing import Optional, Dict, Any
import asyncio
import logging

from ..core.base import BaseStreamReader
from ..core.interfaces import IStreamReader

logger = logging.getLogger(__name__)

class RTSPStreamReader(BaseStreamReader, IStreamReader):
    """Implementação de leitor RTSP (Single Responsibility)"""
    
    def __init__(
        self, 
        stream_url: str,
        reconnect_attempts: int = 3,
        reconnect_delay: int = 5
    ):
        super().__init__(stream_url)
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay
        self._capture: Optional[cv2.VideoCapture] = None
    
    async def _pre_connect(self) -> bool:
        """Valida URL antes de conectar"""
        if not self.stream_url.startswith(('rtsp://', 'rtmp://', 'http://')):
            logger.error(f"URL inválida: {self.stream_url}")
            return False
        return True
    
    async def _do_connect(self) -> bool:
        """Conecta ao stream RTSP"""
        for attempt in range(self.reconnect_attempts):
            try:
                self._capture = cv2.VideoCapture(self.stream_url)
                
                if self._capture.isOpened():
                    # Lê propriedades
                    self._properties = {
                        "width": int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                        "height": int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                        "fps": int(self._capture.get(cv2.CAP_PROP_FPS)),
                        "codec": int(self._capture.get(cv2.CAP_PROP_FOURCC))
                    }
                    return True
                
                logger.warning(f"Tentativa {attempt + 1} falhou")
                await asyncio.sleep(self.reconnect_delay)
                
            except Exception as e:
                logger.error(f"Erro na tentativa {attempt + 1}: {str(e)}")
                await asyncio.sleep(self.reconnect_delay)
        
        return False
    
    async def _do_read_frame(self) -> Optional[np.ndarray]:
        """Lê frame do stream"""
        if not self._capture or not self._capture.isOpened():
            return None
        
        ret, frame = self._capture.read()
        return frame if ret else None
    
    async def _do_disconnect(self) -> None:
        """Desconecta do stream"""
        if self._capture:
            self._capture.release()
            self._capture = None


class FileStreamReader(BaseStreamReader, IStreamReader):
    """Implementação de leitor de arquivo (Single Responsibility)"""
    
    def __init__(self, file_path: str, loop: bool = False):
        super().__init__(file_path)
        self.loop = loop
        self._capture: Optional[cv2.VideoCapture] = None
    
    async def _do_connect(self) -> bool:
        """Abre arquivo de vídeo"""
        try:
            self._capture = cv2.VideoCapture(self.stream_url)
            
            if self._capture.isOpened():
                self._properties = {
                    "width": int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    "height": int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                    "fps": int(self._capture.get(cv2.CAP_PROP_FPS)),
                    "total_frames": int(self._capture.get(cv2.CAP_PROP_FRAME_COUNT))
                }
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao abrir arquivo: {str(e)}")
            return False
    
    async def _do_read_frame(self) -> Optional[np.ndarray]:
        """Lê frame do arquivo"""
        if not self._capture or not self._capture.isOpened():
            return None
        
        ret, frame = self._capture.read()
        
        # Se chegou ao fim e loop está ativo, reinicia
        if not ret and self.loop:
            self._capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._capture.read()
        
        return frame if ret else None
    
    async def _do_disconnect(self) -> None:
        """Fecha arquivo"""
        if self._capture:
            self._capture.release()
            self._capture = None