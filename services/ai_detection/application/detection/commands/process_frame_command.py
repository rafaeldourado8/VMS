from dataclasses import dataclass
from typing import Optional


@dataclass
class ProcessFrameCommand:
    """Command para processar um frame de vídeo"""
    
    camera_id: int
    frame_data: bytes
    timestamp: float
    enable_ocr: bool = False
