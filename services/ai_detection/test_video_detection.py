"""
Teste de Detecção com Vídeo Local
Processa vídeo de carros e envia detecções para o backend
"""
import cv2
import numpy as np
import requests
import logging
from datetime import datetime
from ultralytics import YOLO
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoDetectionTest:
    def __init__(self, video_path: str, camera_id: int = 1):
        self.video_path = video_path
        self.camera_id = camera_id
        self.model = YOLO('/app/yolov8n.pt')
        self.backend_url = "http://backend:8000/api/deteccoes/ingest/"
        self.api_key = "your-ingest-api-key-here"
        logger.info(f"✅ Teste inicializado - Vídeo: {video_path}")
    
    def process_video(self):
        """Processa vídeo e detecta veículos"""
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            logger.error(f"❌ Não foi possível abrir vídeo: {self.video_path}")
            return
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        logger.info(f"📹 Vídeo: {total_frames} frames @ {fps} FPS")
        
        frame_count = 0
        detections_sent = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Processa a cada 30 frames (1 por segundo)
            if frame_count % 30 != 0:
                continue
            
            logger.info(f"🔍 Processando frame {frame_count}/{total_frames}")
            
            # Detecta veículos
            results = self.model(frame, verbose=False, classes=[2, 3, 5, 7])
            
            if len(results) > 0 and len(results[0].boxes) > 0:
                for box in results[0].boxes:
                    bbox = box.xyxy[0].cpu().numpy().astype(int)
                    x1, y1, x2, y2 = bbox
                    w, h = x2 - x1, y2 - y1
                    
                    # Filtra detecções pequenas
                    if w < 50 or h < 50:
                        continue
                    
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                    # Só envia se confiança alta
                    if confidence > 0.5:
                        vehicle_crop = frame[y1:y2, x1:x2]
                        success = self._send_detection(
                            confidence, class_id, vehicle_crop
                        )
                        if success:
                            detections_sent += 1
                            logger.info(f"✅ Detecção {detections_sent} enviada (conf: {confidence:.2f})")
        
        cap.release()
        logger.info(f"🏁 Processamento concluído: {detections_sent} detecções enviadas")
    
    def _send_detection(self, confidence: float, class_id: int, vehicle_crop):
        """Envia detecção para o backend"""
        try:
            # Comprime imagem
            _, buffer = cv2.imencode('.jpg', vehicle_crop, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            vehicle_types = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}
            vehicle_type = vehicle_types.get(class_id, 'car')
            
            files = {
                'image': ('detection.jpg', buffer.tobytes(), 'image/jpeg')
            }
            
            data = {
                'camera_id': self.camera_id,
                'timestamp': datetime.now().isoformat(),
                'plate': f"TEST{np.random.randint(1000, 9999)}",
                'confidence': confidence,
                'vehicle_type': vehicle_type
            }
            
            headers = {'X-API-Key': self.api_key}
            
            response = requests.post(
                self.backend_url,
                data=data,
                files=files,
                headers=headers,
                timeout=5
            )
            
            return response.status_code == 201
            
        except Exception as e:
            logger.error(f"❌ Erro enviando detecção: {e}")
            return False

if __name__ == "__main__":
    # Testa com vídeo na raiz do projeto
    video_path = "/app/../video_carros.mp4"  # Ajuste o nome do arquivo
    
    logger.info("🚀 Iniciando teste de detecção com vídeo local")
    logger.info(f"📁 Vídeo: {video_path}")
    
    tester = VideoDetectionTest(video_path, camera_id=1)
    tester.process_video()
