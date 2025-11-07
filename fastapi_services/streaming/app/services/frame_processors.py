# fastapi_services/streaming/app/services/frame_processors.py
import cv2
import numpy as np
from typing import Tuple, Optional
import logging

from ..core.base import BaseFrameProcessor
from ..core.interfaces import IFrameProcessor

logger = logging.getLogger(__name__)

class ResizeProcessor(BaseFrameProcessor, IFrameProcessor):
    """Processador de redimensionamento (Single Responsibility)"""
    
    def __init__(self, max_width: int = 1280, max_height: Optional[int] = None):
        super().__init__()
        self.max_width = max_width
        self.max_height = max_height
    
    async def _do_process(self, frame: np.ndarray) -> np.ndarray:
        """Redimensiona frame mantendo aspect ratio"""
        height, width = frame.shape[:2]
        
        # Calcula nova dimensão
        if width > self.max_width:
            scale = self.max_width / width
            new_width = self.max_width
            new_height = int(height * scale)
            
            if self.max_height and new_height > self.max_height:
                scale = self.max_height / new_height
                new_height = self.max_height
                new_width = int(new_width * scale)
            
            frame = cv2.resize(frame, (new_width, new_height))
        
        return frame


class QualityProcessor(BaseFrameProcessor, IFrameProcessor):
    """Processador de qualidade (Single Responsibility)"""
    
    def __init__(self, quality: int = 80):
        super().__init__()
        self.quality = max(1, min(100, quality))
    
    async def _do_process(self, frame: np.ndarray) -> np.ndarray:
        """Ajusta qualidade do frame"""
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
        _, encoded = cv2.imencode('.jpg', frame, encode_param)
        decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        return decoded


class WatermarkProcessor(BaseFrameProcessor, IFrameProcessor):
    """Processador de marca d'água (Single Responsibility)"""
    
    def __init__(
        self, 
        text: str = "VMS", 
        position: Tuple[int, int] = (10, 30),
        font_scale: float = 1.0,
        color: Tuple[int, int, int] = (255, 255, 255),
        thickness: int = 2
    ):
        super().__init__()
        self.text = text
        self.position = position
        self.font_scale = font_scale
        self.color = color
        self.thickness = thickness
    
    async def _do_process(self, frame: np.ndarray) -> np.ndarray:
        """Adiciona marca d'água ao frame"""
        cv2.putText(
            frame,
            self.text,
            self.position,
            cv2.FONT_HERSHEY_SIMPLEX,
            self.font_scale,
            self.color,
            self.thickness
        )
        return frame


class TimestampProcessor(BaseFrameProcessor, IFrameProcessor):
    """Processador de timestamp (Single Responsibility)"""
    
    def __init__(
        self,
        position: Tuple[int, int] = (10, 30),
        font_scale: float = 0.7,
        color: Tuple[int, int, int] = (255, 255, 255),
        thickness: int = 2,
        format: str = "%Y-%m-%d %H:%M:%S"
    ):
        super().__init__()
        self.position = position
        self.font_scale = font_scale
        self.color = color
        self.thickness = thickness
        self.format = format
    
    async def _do_process(self, frame: np.ndarray) -> np.ndarray:
        """Adiciona timestamp ao frame"""
        from datetime import datetime
        timestamp = datetime.now().strftime(self.format)
        
        cv2.putText(
            frame,
            timestamp,
            self.position,
            cv2.FONT_HERSHEY_SIMPLEX,
            self.font_scale,
            self.color,
            self.thickness
        )
        return frame


class BlurProcessor(BaseFrameProcessor, IFrameProcessor):
    """Processador de desfoque (Single Responsibility)"""
    
    def __init__(self, kernel_size: int = 5):
        super().__init__()
        self.kernel_size = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    
    async def _do_process(self, frame: np.ndarray) -> np.ndarray:
        """Aplica desfoque gaussiano"""
        return cv2.GaussianBlur(frame, (self.kernel_size, self.kernel_size), 0)


class GrayscaleProcessor(BaseFrameProcessor, IFrameProcessor):
    """Processador de escala de cinza (Single Responsibility)"""
    
    async def _do_process(self, frame: np.ndarray) -> np.ndarray:
        """Converte para escala de cinza"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


class BrightnessProcessor(BaseFrameProcessor, IFrameProcessor):
    """Processador de brilho (Single Responsibility)"""
    
    def __init__(self, brightness: int = 0):
        super().__init__()
        self.brightness = max(-100, min(100, brightness))
    
    async def _do_process(self, frame: np.ndarray) -> np.ndarray:
        """Ajusta brilho do frame"""
        if self.brightness == 0:
            return frame
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        if self.brightness > 0:
            lim = 255 - self.brightness
            v[v > lim] = 255
            v[v <= lim] += self.brightness
        else:
            lim = abs(self.brightness)
            v[v < lim] = 0
            v[v >= lim] -= abs(self.brightness)
        
        final_hsv = cv2.merge((h, s, v))
        return cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)