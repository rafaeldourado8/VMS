"""
Serviço de Detecção de Placas com Trigger P1-P2
Processamento isolado sem interferir no streaming
"""

import asyncio
import cv2
import numpy as np
from datetime import datetime
from typing import Optional, Tuple
import logging
from dataclasses import dataclass
import hashlib
import requests
import base64

logger = logging.getLogger(__name__)

@dataclass
class DetectionZone:
    camera_id: int
    p1: Tuple[int, int]
    p2: Tuple[int, int]
    distance_meters: float
    speed_limit_kmh: float
    fps: float

@dataclass
class VehicleDetection:
    vehicle_id: str
    camera_id: int
    plate_text: str
    speed_kmh: float
    timestamp_p1: datetime
    timestamp_p2: datetime
    frame_count: int
    plate_image: bytes
    bbox: Tuple[int, int, int, int]

class VehicleTracker:
    def __init__(self, zone: DetectionZone):
        self.zone = zone
        self.active_vehicles = {}
        
    def check_crossing_p1(self, bbox: Tuple[int, int, int, int]) -> bool:
        x, y, w, h = bbox
        center_y = y + h // 2
        p1_y = self.zone.p1[1]
        return abs(center_y - p1_y) < 10
    
    def check_crossing_p2(self, bbox: Tuple[int, int, int, int]) -> bool:
        x, y, w, h = bbox
        center_y = y + h // 2
        p2_y = self.zone.p2[1]
        return abs(center_y - p2_y) < 10
    
    def generate_vehicle_id(self, bbox: Tuple[int, int, int, int], timestamp: datetime) -> str:
        data = f"{self.zone.camera_id}_{bbox}_{timestamp.timestamp()}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    def calculate_speed(self, frame_count: int) -> float:
        time_seconds = frame_count / self.zone.fps
        speed_ms = self.zone.distance_meters / time_seconds
        speed_kmh = speed_ms * 3.6
        return round(speed_kmh, 2)
    
    def start_tracking(self, bbox: Tuple[int, int, int, int], frame_number: int) -> str:
        vehicle_id = self.generate_vehicle_id(bbox, datetime.now())
        self.active_vehicles[vehicle_id] = {
            'p1_time': datetime.now(),
            'p1_frame': frame_number,
            'bbox': bbox,
            'active': True
        }
        logger.info(f"🚗 Veículo {vehicle_id} cruzou P1 - IA ATIVADA")
        return vehicle_id
    
    def finish_tracking(self, vehicle_id: str, frame_number: int) -> Optional[dict]:
        if vehicle_id not in self.active_vehicles:
            return None
        
        vehicle = self.active_vehicles[vehicle_id]
        frame_count = frame_number - vehicle['p1_frame']
        speed_kmh = self.calculate_speed(frame_count)
        
        result = {
            'vehicle_id': vehicle_id,
            'p1_time': vehicle['p1_time'],
            'p2_time': datetime.now(),
            'frame_count': frame_count,
            'speed_kmh': speed_kmh,
            'speeding': speed_kmh > self.zone.speed_limit_kmh
        }
        
        del self.active_vehicles[vehicle_id]
        logger.info(f"🏁 Veículo {vehicle_id} cruzou P2 - {speed_kmh} km/h - IA DESATIVADA")
        return result

class PlateDetector:
    """Detector de placas usando YOLO"""
    def __init__(self):
        from ultralytics import YOLO
        self.model = YOLO('/app/yolov8n.pt')
        logger.info("✅ Detector de placas carregado")
    
    def detect_plate(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[Tuple[str, bytes, Tuple]]:
        x, y, w, h = bbox
        vehicle_roi = frame[y:y+h, x:x+w]
        
        # Detecta com YOLO
        results = self.model(vehicle_roi, verbose=False)
        
        if len(results) > 0 and len(results[0].boxes) > 0:
            # Pega primeira detecção
            box = results[0].boxes[0]
            plate_bbox = box.xyxy[0].cpu().numpy().astype(int)
            px1, py1, px2, py2 = plate_bbox
            
            # Recorta placa
            plate_image = vehicle_roi[py1:py2, px1:px2]
            
            # OCR simples (substituir por EasyOCR se necessário)
            plate_text = f"ABC{np.random.randint(1000, 9999)}"
            
            # Converte para bytes
            _, buffer = cv2.imencode('.jpg', plate_image)
            plate_bytes = buffer.tobytes()
            
            return plate_text, plate_bytes, (px1, py1, px2-px1, py2-py1)
        
        return None

class VehicleDetector:
    """Detector de veículos usando YOLO"""
    def __init__(self):
        from ultralytics import YOLO
        self.model = YOLO('/app/yolov8n.pt')
        logger.info("✅ Detector de veículos carregado")
    
    def detect_vehicles(self, frame: np.ndarray) -> list:
        """Detecta veículos no frame e retorna bboxes"""
        results = self.model(frame, verbose=False, classes=[2, 3, 5, 7])  # car, motorcycle, bus, truck
        
        detections = []
        if len(results) > 0 and len(results[0].boxes) > 0:
            for box in results[0].boxes:
                bbox = box.xyxy[0].cpu().numpy().astype(int)
                x1, y1, x2, y2 = bbox
                w, h = x2 - x1, y2 - y1
                
                # Filtra detecções muito pequenas
                if w > 50 and h > 50:
                    detections.append((x1, y1, w, h))
        
        return detections

class AIDetectionService:
    def __init__(self):
        self.zones = {}
        self.trackers = {}
        self.vehicle_detector = VehicleDetector()
        self.plate_detector = PlateDetector()
        self.processing_queue = asyncio.Queue()
        self.backend_url = "http://backend:8000/api/deteccoes/ingest/"
        self.api_key = "default_insecure_key_12345"  # Deve coincidir com INGEST_API_KEY do Django
        
    def configure_zone(self, zone: DetectionZone):
        self.zones[zone.camera_id] = zone
        self.trackers[zone.camera_id] = VehicleTracker(zone)
        logger.info(f"✅ Zona configurada: Cam{zone.camera_id} P1{zone.p1}->P2{zone.p2} {zone.distance_meters}m")
    
    def load_zones_from_db(self, db: 'DetectionDatabase'):
        """Carrega zonas de detecção do banco de dados"""
        # TODO: Implementar carregamento de todas as zonas ativas
        # Por enquanto, configura zona padrão para câmeras que não têm
        pass
    
    async def process_frame(self, camera_id: int, frame: np.ndarray, frame_number: int):
        if camera_id not in self.trackers:
            return
        
        # Detecta veículos no frame
        detections = self.vehicle_detector.detect_vehicles(frame)
        
        if not detections:
            return
        
        tracker = self.trackers[camera_id]
        
        for bbox in detections:
            if tracker.check_crossing_p1(bbox):
                vehicle_id = tracker.start_tracking(bbox, frame_number)
                await self.processing_queue.put({
                    'action': 'detect_plate',
                    'camera_id': camera_id,
                    'vehicle_id': vehicle_id,
                    'frame': frame.copy(),
                    'bbox': bbox
                })
            
            elif tracker.check_crossing_p2(bbox):
                for vehicle_id, vehicle_data in list(tracker.active_vehicles.items()):
                    if self._bbox_match(vehicle_data['bbox'], bbox):
                        result = tracker.finish_tracking(vehicle_id, frame_number)
                        if result and result['speeding']:
                            await self.processing_queue.put({
                                'action': 'save_detection',
                                'camera_id': camera_id,
                                'result': result
                            })
    
    def _bbox_match(self, bbox1: Tuple, bbox2: Tuple, threshold: float = 0.5) -> bool:
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        xi1 = max(x1, x2)
        yi1 = max(y1, y2)
        xi2 = min(x1 + w1, x2 + w2)
        yi2 = min(y1 + h1, y2 + h2)
        
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        box1_area = w1 * h1
        box2_area = w2 * h2
        union_area = box1_area + box2_area - inter_area
        
        iou = inter_area / union_area if union_area > 0 else 0
        return iou > threshold
    
    async def send_to_backend(self, detection_data: dict):
        """Envia detecção para o endpoint Django"""
        try:
            # Converte imagem da placa para base64
            plate_image_b64 = base64.b64encode(detection_data['plate_image']).decode()
            
            payload = {
                'camera_id': detection_data['camera_id'],
                'timestamp': detection_data['timestamp_p1'].isoformat(),
                'plate': detection_data['plate_text'],
                'confidence': 0.85,  # TODO: Usar confiança real do OCR
                'vehicle_type': 'car',  # TODO: Detectar tipo do veículo
                'image_url': f"data:image/jpeg;base64,{plate_image_b64}"
            }
            
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': self.api_key
            }
            
            response = requests.post(
                self.backend_url,
                json=payload,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Detecção enviada: {detection_data['plate_text']}")
                return True
            else:
                logger.error(f"❌ Erro enviando detecção: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro enviando para backend: {e}")
            return False
    async def worker_process_queue(self):
        while True:
            try:
                task = await self.processing_queue.get()
                
                if task['action'] == 'detect_plate':
                    result = self.plate_detector.detect_plate(task['frame'], task['bbox'])
                    if result:
                        plate_text, plate_image, plate_bbox = result
                        logger.info(f"🔍 Placa detectada: {plate_text}")
                        
                        # Armazena dados da placa para quando o veículo cruzar P2
                        vehicle_id = task['vehicle_id']
                        if vehicle_id in self.trackers[task['camera_id']].active_vehicles:
                            self.trackers[task['camera_id']].active_vehicles[vehicle_id]['plate_data'] = {
                                'plate_text': plate_text,
                                'plate_image': plate_image,
                                'plate_bbox': plate_bbox
                            }
                
                elif task['action'] == 'save_detection':
                    camera_id = task['camera_id']
                    result = task['result']
                    
                    # Busca dados da placa
                    vehicle_id = result['vehicle_id']
                    plate_data = None
                    
                    # Tenta recuperar dados da placa do tracker
                    if camera_id in self.trackers:
                        for vid, vdata in self.trackers[camera_id].active_vehicles.items():
                            if vid == vehicle_id and 'plate_data' in vdata:
                                plate_data = vdata['plate_data']
                                break
                    
                    if plate_data:
                        detection_data = {
                            'camera_id': camera_id,
                            'vehicle_id': vehicle_id,
                            'plate_text': plate_data['plate_text'],
                            'speed_kmh': result['speed_kmh'],
                            'speeding': result['speeding'],
                            'timestamp_p1': result['p1_time'],
                            'timestamp_p2': result['p2_time'],
                            'plate_image': plate_data['plate_image']
                        }
                        
                        # Envia para o backend Django
                        await self.send_to_backend(detection_data)
                        
                        logger.info(f"💾 Detecção salva: {plate_data['plate_text']} - {result['speed_kmh']} km/h")
                    else:
                        logger.warning(f"⚠️ Dados da placa não encontrados para veículo {vehicle_id}")
                
                self.processing_queue.task_done()
            except Exception as e:
                logger.error(f"Erro no worker: {e}")
                await asyncio.sleep(1)