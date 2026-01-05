import numpy as np
from typing import Optional, Dict
from domain.detection.value_objects.bounding_box import BoundingBox


class OCREngine:
    """Wrapper minimalista para OCR de placas"""
    
    def __init__(self, conf_threshold: float = 0.7):
        self.conf_threshold = conf_threshold
        try:
            import easyocr
            self.reader = easyocr.Reader(['pt'], gpu=False)
        except ImportError:
            self.reader = None
    
    def detect_plate(self, frame: bytes, bbox: BoundingBox) -> Optional[Dict[str, any]]:
        """Detecta placa na região do bounding box"""
        if not self.reader:
            return None
        
        # Converte bytes para numpy array
        nparr = np.frombuffer(frame, np.uint8)
        
        # Recorta região do veículo
        x, y, w, h = int(bbox.x), int(bbox.y), int(bbox.width), int(bbox.height)
        roi = nparr[y:y+h, x:x+w]
        
        # Executa OCR
        results = self.reader.readtext(roi)
        
        # Filtra resultados
        for (box, text, conf) in results:
            if conf >= self.conf_threshold and self._is_valid_plate(text):
                return {
                    'plate': self._normalize_plate(text),
                    'confidence': conf
                }
        
        return None
    
    def _is_valid_plate(self, text: str) -> bool:
        """Valida formato de placa brasileira"""
        text = text.upper().replace(' ', '').replace('-', '')
        if len(text) != 7:
            return False
        return text[:3].isalpha() and text[3:].replace('0', '').replace('1', '').isdigit()
    
    def _normalize_plate(self, text: str) -> str:
        """Normaliza placa"""
        return text.upper().replace(' ', '').replace('-', '')
