"""
Testa deteccao na camera ID 2 (Teste 02)
Captura do HLS e envia deteccoes
"""
import cv2
import requests
import time
from datetime import datetime
import numpy as np

BACKEND_URL = "http://backend:8000/api/ingest/"
API_KEY = "your-ingest-api-key-here"
CAMERA_ID = 2
HLS_URL = "http://mediamtx:8889/cam_2/index.m3u8"

def test_camera():
    print(f"Testando camera {CAMERA_ID}")
    print(f"URL: {HLS_URL}")
    
    cap = cv2.VideoCapture(HLS_URL)
    
    if not cap.isOpened():
        print("ERRO: Nao conectou ao stream")
        return
    
    print("Conectado! Processando...")
    frame_count = 0
    detections = 0
    
    while detections < 5:  # Envia 5 deteccoes
        ret, frame = cap.read()
        if not ret:
            print("Erro ao ler frame")
            time.sleep(1)
            continue
        
        frame_count += 1
        
        # Processa a cada 30 frames
        if frame_count % 30 != 0:
            continue
        
        # Pega regiao central
        h, w = frame.shape[:2]
        x1, y1 = w // 4, h // 4
        x2, y2 = 3 * w // 4, 3 * h // 4
        crop = frame[y1:y2, x1:x2]
        
        # Envia
        if send_detection(crop):
            detections += 1
            print(f"Deteccao {detections}/5 enviada")
    
    cap.release()
    print(f"\nConcluido! {detections} deteccoes enviadas")

def send_detection(image):
    try:
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        files = {'image': ('det.jpg', buffer.tobytes(), 'image/jpeg')}
        data = {
            'camera_id': CAMERA_ID,
            'timestamp': datetime.now().isoformat(),
            'plate': f"TEST{np.random.randint(1000,9999)}",
            'confidence': 0.90,
            'vehicle_type': 'car'
        }
        headers = {'X-API-Key': API_KEY}
        
        response = requests.post(BACKEND_URL, data=data, files=files, headers=headers, timeout=5)
        
        if response.status_code == 201:
            return True
        else:
            print(f"  Erro: {response.status_code}")
            return False
    except Exception as e:
        print(f"  Erro: {e}")
        return False

test_camera()
