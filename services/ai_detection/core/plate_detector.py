import cv2
import numpy as np
import logging
from ultralytics import YOLO

class PlateDetector:
    def __init__(self, model_path: str, confidence: float = 0.6):
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.logger = logging.getLogger(__name__)
    
    def detect(self, frame: np.ndarray) -> list:
        results = self.model(frame, conf=self.confidence, verbose=False)
        
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                
                detections.append({
                    'bbox': (x1, y1, x2, y2),
                    'confidence': conf,
                    'crop': frame[y1:y2, x1:x2]
                })
        
        return detections
