# fastapi_services/streaming/app/services/frame_encoder.py
import cv2
import numpy as np
import base64
from typing import Optional
import logging

from ..core.interfaces import IFrameEncoder

logger = logging.getLogger(__name__)

class JPEGEncoder(IFrameEncoder):
    """Encoder JPEG (Single Responsibility)"""
    
    def __init__(self, quality: int = 80):
        self.quality = max(1, min(100, quality))
        self._encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
    
    async def encode(self, frame: np.ndarray) -> bytes:
        """Codifica frame para JPEG"""
        try:
            _, buffer = cv2.imencode('.jpg', frame, self._encode_params)
            return buffer.tobytes()
        except Exception as e:
            logger.error(f"Erro ao codificar frame: {str(e)}")
            raise


class Base64Encoder(IFrameEncoder):
    """Encoder Base64 (Single Responsibility)"""
    
    def __init__(self, quality: int = 80):
        self.jpeg_encoder = JPEGEncoder(quality)
    
    async def encode(self, frame: np.ndarray) -> bytes:
        """Codifica frame para Base64"""
        try:
            jpeg_bytes = await self.jpeg_encoder.encode(frame)
            base64_bytes = base64.b64encode(jpeg_bytes)
            return base64_bytes
        except Exception as e:
            logger.error(f"Erro ao codificar para base64: {str(e)}")
            raise


class MJPEGEncoder(IFrameEncoder):
    """Encoder MJPEG (Single Responsibility)"""
    
    def __init__(self, quality: int = 80):
        self.jpeg_encoder = JPEGEncoder(quality)
    
    async def encode(self, frame: np.ndarray) -> bytes:
        """Codifica frame para MJPEG stream"""
        try:
            jpeg_bytes = await self.jpeg_encoder.encode(frame)
            
            # Formato MJPEG multipart
            return (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n'
            )
        except Exception as e:
            logger.error(f"Erro ao codificar MJPEG: {str(e)}")
            raise