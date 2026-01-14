from abc import ABC, abstractmethod
import numpy as np

class IDetectionProvider(ABC):
    """Interface para provedor de detecção (YOLO + OCR)"""
    
    @abstractmethod
    def detect_plates(self, frame: np.ndarray) -> list[dict]:
        """
        Detecta placas em um frame
        Returns: [{'plate': 'ABC1234', 'confidence': 0.95, 'bbox': [x,y,w,h]}]
        """
        pass
