"""
Worker simples - Processa cameras RTSP e envia deteccoes
"""
import cv2
import requests
import time
from datetime import datetime
import numpy as np

BACKEND_URL = "http://backend:8000/api/ingest/"
API_KEY = "your-ingest-api-key-here"

CAMERAS = [
    {"id": 3, "url": "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0"},
    {"id": 4, "url": "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0"},
    {"id": 5, "url": "rtsp://admin:Camerite123@45.236.226.74:6050/cam/realmonitor?channel=1&subtype=0"},
]

def process_camera(camera_id, rtsp_url):
    """Processa uma camera"""
    print(f"Conectando camera {camera_id}...")
    cap = cv2.VideoCapture(rtsp_url)
    
    if not cap.isOpened():
        print(f"  ERRO: Nao conectou")
        return
    
    print(f"  OK - Processando...")
    frame_count = 0
    detections = 0
    
    while frame_count < 300:  # 10 segundos a 30fps
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Processa a cada 30 frames (1 por segundo)
        if frame_count % 30 != 0:
            continue
        
        # Pega regiao central
        h, w = frame.shape[:2]
        x1, y1 = w // 4, h // 4
        x2, y2 = 3 * w // 4, 3 * h // 4
        crop = frame[y1:y2, x1:x2]
        
        # Envia
        if send_detection(camera_id, crop):
            detections += 1
            print(f"  Deteccao {detections} enviada")
    
    cap.release()
    print(f"Camera {camera_id}: {detections} deteccoes")

def send_detection(camera_id, image):
    """Envia deteccao"""
    try:
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        files = {'image': ('det.jpg', buffer.tobytes(), 'image/jpeg')}
        data = {
            'camera_id': camera_id,
            'timestamp': datetime.now().isoformat(),
            'plate': f"CAM{camera_id}{np.random.randint(100,999)}",
            'confidence': 0.85,
            'vehicle_type': 'car'
        }
        headers = {'X-API-Key': API_KEY}
        
        response = requests.post(BACKEND_URL, data=data, files=files, headers=headers, timeout=5)
        return response.status_code == 201
    except:
        return False

print("Iniciando processamento...")
for cam in CAMERAS:
    process_camera(cam['id'], cam['url'])
    time.sleep(2)

print("\nConcluido!")
