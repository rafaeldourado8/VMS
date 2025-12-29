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
    def detect_plate(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[Tuple[str, bytes, Tuple]]:
        x, y, w, h = bbox
        vehicle_roi = frame[y:y+h, x:x+w]
        
        # STUB: Integrar modelo real aqui
        plate_text = "ABC1234"
        plate_bbox = (10, 10, 100, 30)
        
        px, py, pw, ph = plate_bbox
        plate_image = vehicle_roi[py:py+ph, px:px+pw]
        
        _, buffer = cv2.imencode('.jpg', plate_image)
        plate_bytes = buffer.tobytes()
        
        return plate_text, plate_bytes, plate_bbox

class AIDetectionService:
    def __init__(self):
        self.zones = {}
        self.trackers = {}
        self.detector = PlateDetector()
        self.processing_queue = asyncio.Queue()
        
    def configure_zone(self, zone: DetectionZone):
        self.zones[zone.camera_id] = zone
        self.trackers[zone.camera_id] = VehicleTracker(zone)
        logger.info(f"✅ Zona configurada: Cam{zone.camera_id} P1{zone.p1}->P2{zone.p2} {zone.distance_meters}m")
    
    async def process_frame(self, camera_id: int, frame: np.ndarray, frame_number: int, detections: list):
        if camera_id not in self.trackers:
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
                for vehicle_id, vehicle_data in tracker.active_vehicles.items():
                    if self._bbox_match(vehicle_data['bbox'], bbox):
                        result = tracker.finish_tracking(vehicle_id, frame_number)
                        if result and result['speeding']:
                            await self.processing_queue.put({
                                'action': 'save_detection',
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
    
    async def worker_process_queue(self):
        while True:
            try:
                task = await self.processing_queue.get()
                
                if task['action'] == 'detect_plate':
                    result = self.detector.detect_plate(task['frame'], task['bbox'])
                    if result:
                        plate_text, plate_image, plate_bbox = result
                        logger.info(f"🔍 Placa detectada: {plate_text}")
                
                elif task['action'] == 'save_detection':
                    logger.info(f"💾 Salvando detecção: {task['result']}")
                
                self.processing_queue.task_done()
            except Exception as e:
                logger.error(f"Erro no worker: {e}")
                await asyncio.sleep(1)