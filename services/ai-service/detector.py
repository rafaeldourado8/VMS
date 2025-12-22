import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple
import logging
import os
from config import settings

logger = logging.getLogger(__name__)

class VehicleDetector:
    def __init__(self):
        self._setup_gpu()
        os.environ['YOLO_VERBOSE'] = 'False'
        self.yolo = YOLO(settings.yolo_model)
        self.lpr_model = self._load_lpr_model()
        self.vehicle_classifier = self._load_vehicle_classifier()
        
    def _setup_gpu(self):
        logger.info(f"GPU mode: {settings.enable_gpu}")
    
    def _load_lpr_model(self):
        logger.warning("LPR model disabled (TensorFlow not installed)")
        return None
    
    def _load_vehicle_classifier(self):
        logger.warning("Vehicle classifier disabled (TensorFlow not installed)")
        return None
    
    def detect(self, image: np.ndarray) -> List[dict]:
        results = self.yolo(image, conf=settings.confidence_threshold, classes=[2, 3, 5, 7])
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                vehicle_crop = image[y1:y2, x1:x2]
                
                detection = {
                    "object_type": self._get_class_name(cls),
                    "confidence": conf,
                    "bbox": {"x": x1, "y": y1, "w": x2-x1, "h": y2-y1},
                    "plate_number": self._detect_plate(vehicle_crop),
                    "vehicle_model": self._classify_vehicle(vehicle_crop)
                }
                detections.append(detection)
        
        return detections
    
    def _get_class_name(self, cls: int) -> str:
        names = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
        return names.get(cls, "vehicle")
    
    def _detect_plate(self, crop: np.ndarray) -> Tuple[str, float]:
        return None, 0.0
    
    def _classify_vehicle(self, crop: np.ndarray) -> Tuple[str, float]:
        return None, 0.0
    
    def _decode_plate(self, pred: np.ndarray) -> str:
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join([chars[i] for i in np.argmax(pred.reshape(-1, len(chars)), axis=1)])[:7]
    
    def _get_vehicle_model(self, idx: int) -> str:
        models = ["sedan", "suv", "pickup", "van", "coupe", "hatchback"]
        return models[idx] if idx < len(models) else "unknown"
