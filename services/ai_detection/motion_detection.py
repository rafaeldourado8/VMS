"""
Motion Detection + ROI + Celery Queue
Processa apenas frames com movimento dentro do ROI
"""
import cv2
import numpy as np
from celery import shared_task
from shapely.geometry import Point, Polygon
import logging

logger = logging.getLogger(__name__)

class MotionDetector:
    """Detecta movimento dentro de ROI"""
    
    def __init__(self, roi_polygon, sensitivity=0.01):
        self.roi = Polygon(roi_polygon)
        self.sensitivity = sensitivity
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=16,
            detectShadows=False
        )
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    
    def has_motion_in_roi(self, frame):
        """Verifica se há movimento dentro do ROI"""
        # 1. Background subtraction
        fg_mask = self.bg_subtractor.apply(frame)
        
        # 2. Morphological operations
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, self.kernel)
        
        # 3. Cria máscara do ROI
        h, w = frame.shape[:2]
        roi_mask = np.zeros((h, w), dtype=np.uint8)
        roi_points = np.array([(int(p[0]*w), int(p[1]*h)) for p in self.roi.exterior.coords], dtype=np.int32)
        cv2.fillPoly(roi_mask, [roi_points], 255)
        
        # 4. Aplica ROI na máscara de movimento
        motion_in_roi = cv2.bitwise_and(fg_mask, roi_mask)
        
        # 5. Conta pixels em movimento
        motion_pixels = cv2.countNonZero(motion_in_roi)
        roi_area = cv2.countNonZero(roi_mask)
        
        # 6. Threshold baseado em % da área ROI
        motion_ratio = motion_pixels / roi_area if roi_area > 0 else 0
        
        return motion_ratio > self.sensitivity


class TriggerChecker:
    """Verifica se detecção ativa triggers"""
    
    @staticmethod
    def check_line_crossing(bbox, line_start, line_end, direction='both'):
        """Verifica se veículo cruzou linha virtual"""
        # Centro do bbox
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        
        # Verifica cruzamento (simplificado)
        # TODO: Implementar tracking para detectar direção real
        return True  # Por enquanto sempre retorna True
    
    @staticmethod
    def check_zone_trigger(bbox, zone_polygon, trigger_type='enter'):
        """Verifica se veículo entrou/saiu de zona"""
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        point = Point(cx, cy)
        zone = Polygon(zone_polygon)
        
        is_inside = zone.contains(point)
        
        if trigger_type == 'enter':
            return is_inside
        elif trigger_type == 'exit':
            return not is_inside
        else:  # both
            return True


@shared_task(bind=True, max_retries=3, queue='detection')
def detect_vehicle_task(self, camera_id, frame_bytes, roi, triggers):
    """
    Task Celery para detectar veículos
    Processa apenas frames com movimento
    """
    try:
        from ultralytics import YOLO
        import requests
        from datetime import datetime
        
        # 1. Decodifica frame
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 2. YOLO detection
        model = YOLO('/app/yolov8n.pt')
        results = model(frame, verbose=False, classes=[2, 3, 5, 7])  # vehicles
        
        if len(results) == 0 or len(results[0].boxes) == 0:
            return {'detections': 0}
        
        # 3. Filtra detecções por ROI
        roi_polygon = Polygon(roi)
        detections_in_roi = []
        
        for box in results[0].boxes:
            bbox = box.xyxy[0].cpu().numpy()
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            
            if roi_polygon.contains(Point(cx, cy)):
                detections_in_roi.append({
                    'bbox': bbox.tolist(),
                    'confidence': float(box.conf[0]),
                    'class_id': int(box.cls[0])
                })
        
        # 4. Verifica triggers
        triggered_detections = []
        for det in detections_in_roi:
            triggered = False
            
            # Virtual lines
            for line in triggers.get('virtual_lines', []):
                if TriggerChecker.check_line_crossing(
                    det['bbox'], 
                    line['start'], 
                    line['end'], 
                    line.get('direction', 'both')
                ):
                    triggered = True
                    break
            
            # Zone triggers
            for zone in triggers.get('zone_triggers', []):
                if TriggerChecker.check_zone_trigger(
                    det['bbox'],
                    zone['points'],
                    zone.get('triggerType', 'enter')
                ):
                    triggered = True
                    break
            
            if triggered:
                triggered_detections.append(det)
        
        # 5. Envia detecções para backend
        for det in triggered_detections:
            # Recorta veículo
            x1, y1, x2, y2 = map(int, det['bbox'])
            vehicle_crop = frame[y1:y2, x1:x2]
            
            # Envia para ingest
            _, buffer = cv2.imencode('.jpg', vehicle_crop, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            files = {'image': ('det.jpg', buffer.tobytes(), 'image/jpeg')}
            data = {
                'camera_id': camera_id,
                'timestamp': datetime.now().isoformat(),
                'plate': f"DET{np.random.randint(1000,9999)}",
                'confidence': det['confidence'],
                'vehicle_type': ['car', 'motorcycle', 'bus', 'truck'][det['class_id'] - 2]
            }
            
            requests.post(
                'http://backend:8000/api/ingest/',
                data=data,
                files=files,
                headers={'X-API-Key': 'your-ingest-api-key-here'},
                timeout=5
            )
        
        logger.info(f"Camera {camera_id}: {len(triggered_detections)} detecções enviadas")
        return {'detections': len(triggered_detections)}
        
    except Exception as e:
        logger.error(f"Erro na detecção: {e}")
        self.retry(exc=e, countdown=5)


class FrameExtractor:
    """Extrai frames e envia para fila quando há movimento"""
    
    def __init__(self, camera_id, rtsp_url, roi, triggers):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.roi = roi
        self.triggers = triggers
        self.motion_detector = MotionDetector(roi)
    
    def start(self):
        """Inicia extração de frames"""
        cap = cv2.VideoCapture(self.rtsp_url)
        frame_count = 0
        
        logger.info(f"Iniciando extração para câmera {self.camera_id}")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning(f"Falha ao ler frame da câmera {self.camera_id}")
                break
            
            frame_count += 1
            
            # Processa apenas 1 frame/segundo
            if frame_count % 30 != 0:
                continue
            
            # Motion detection (rápido, <10ms)
            if self.motion_detector.has_motion_in_roi(frame):
                # Envia para fila Celery
                _, buffer = cv2.imencode('.jpg', frame)
                detect_vehicle_task.delay(
                    self.camera_id,
                    buffer.tobytes(),
                    self.roi,
                    self.triggers
                )
        
        cap.release()
