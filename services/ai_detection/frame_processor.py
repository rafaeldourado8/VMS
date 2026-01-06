"""
Frame Processor - Processa frames e detecta veículos com YOLO
"""
import asyncio
import cv2
import numpy as np
from datetime import datetime
from typing import Optional
import logging
import requests
from ultralytics import YOLO

logger = logging.getLogger(__name__)

class FrameProcessor:
    def __init__(self):
        self.model = YOLO('/app/yolov8n.pt')
        self.active_cameras = {}
        self.backend_url = "http://backend:8000/api/deteccoes/ingest/"
        self.api_key = "default_insecure_key_12345"
        logger.info("✅ Frame Processor inicializado com YOLO")
    
    def start_camera(self, camera_id: int, config: dict):
        """Inicia processamento para uma câmera"""
        self.active_cameras[camera_id] = {
            'config': config,
            'last_detection': None,
            'frame_count': 0
        }
        logger.info(f"📹 Câmera {camera_id} ativada para detecção")
    
    def stop_camera(self, camera_id: int):
        """Para processamento para uma câmera"""
        if camera_id in self.active_cameras:
            del self.active_cameras[camera_id]
            logger.info(f"🛑 Câmera {camera_id} desativada")
    
    def process_frame(self, camera_id: int, frame: np.ndarray) -> list:
        """Processa um frame e retorna detecções"""
        if camera_id not in self.active_cameras:
            return []
        
        camera_data = self.active_cameras[camera_id]
        camera_data['frame_count'] += 1
        
        # Detecta veículos com YOLO
        results = self.model(frame, verbose=False, classes=[2, 3, 5, 7])  # car, motorcycle, bus, truck
        
        detections = []
        if len(results) > 0 and len(results[0].boxes) > 0:
            for box in results[0].boxes:
                bbox = box.xyxy[0].cpu().numpy().astype(int)
                x1, y1, x2, y2 = bbox
                w, h = x2 - x1, y2 - y1
                
                # Filtra detecções pequenas
                if w > 50 and h > 50:
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                    detection = {
                        'bbox': (x1, y1, w, h),
                        'confidence': confidence,
                        'class_id': class_id,
                        'timestamp': datetime.now()
                    }
                    detections.append(detection)
                    
                    # Envia para backend se confiança alta
                    if confidence > 0.7:
                        self._send_detection(camera_id, detection, frame[y1:y2, x1:x2])
        
        return detections
    
    def _send_detection(self, camera_id: int, detection: dict, vehicle_crop: np.ndarray):
        """Envia detecção para o backend Django"""
        try:
            # Converte imagem para bytes
            _, buffer = cv2.imencode('.jpg', vehicle_crop, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            vehicle_types = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}
            vehicle_type = vehicle_types.get(detection['class_id'], 'car')
            
            # Prepara multipart form data
            files = {
                'image': ('detection.jpg', buffer.tobytes(), 'image/jpeg')
            }
            
            data = {
                'camera_id': camera_id,
                'timestamp': detection['timestamp'].isoformat(),
                'plate': f"DET{np.random.randint(1000, 9999)}",
                'confidence': detection['confidence'],
                'vehicle_type': vehicle_type
            }
            
            headers = {
                'X-API-Key': self.api_key
            }
            
            response = requests.post(
                self.backend_url,
                data=data,
                files=files,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Detecção enviada: Câmera {camera_id} - {vehicle_type} ({detection['confidence']:.2f})")
            else:
                logger.error(f"❌ Erro enviando detecção: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Erro enviando detecção: {e}")

# Instância global
frame_processor = FrameProcessor()
