import numpy as np
from typing import List, Dict, Any
from domain.detection.value_objects.bounding_box import BoundingBox


class YOLODetector:
    """Wrapper minimalista para YOLOv8"""
    
    def __init__(self, model_path: str = "yolov8n.pt", conf_threshold: float = 0.5):
        self.conf_threshold = conf_threshold
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
        except ImportError:
            self.model = None
    
    def detect(self, frame: bytes) -> List[Dict[str, Any]]:
        """Detecta veículos no frame"""
        if not self.model:
            return []
        
        # Converte bytes para numpy array
        nparr = np.frombuffer(frame, np.uint8)
        
        # Executa detecção
        results = self.model(nparr, conf=self.conf_threshold, classes=[2, 3, 5, 7])  # car, motorcycle, bus, truck
        
        detections = []
        for r in results:
            boxes = r.boxes
            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                bbox = BoundingBox(
                    x=x1,
                    y=y1,
                    width=x2 - x1,
                    height=y2 - y1
                )
                
                detections.append({
                    'track_id': i,  # Simplificado, usar tracker real em produção
                    'bbox': bbox,
                    'confidence': conf,
                    'class': self._get_class_name(cls)
                })
        
        return detections
    
    def _get_class_name(self, cls: int) -> str:
        """Mapeia classe COCO para tipo de veículo"""
        mapping = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}
        return mapping.get(cls, 'unknown')
