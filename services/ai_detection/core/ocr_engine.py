import logging
from fast_plate_ocr.inference.plate_recognizer import LicensePlateRecognizer

class OCREngine:
    def __init__(self, model: str = "cct-xs-v1-global-model"):
        self.recognizer = LicensePlateRecognizer(hub_ocr_model=model)
        self.logger = logging.getLogger(__name__)
    
    def recognize(self, crops: list) -> list:
        if not crops:
            return []
        
        try:
            texts = self.recognizer.run(crops)
            results = []
            
            for i, text in enumerate(texts):
                if text and len(text) >= 7:
                    results.append({
                        'plate': text,
                        'confidence': 0.85  # Fast-Plate-OCR não retorna confidence
                    })
            
            return results
        except Exception as e:
            self.logger.error(f"OCR error: {e}")
            return []
