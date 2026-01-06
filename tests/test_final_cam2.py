"""
Teste final - Camera 2
"""
import cv2
import requests
from datetime import datetime
import numpy as np

BACKEND_URL = "http://backend:8000/api/ingest/"
API_KEY = "your-ingest-api-key-here"
CAMERA_ID = 2
RTSP_URL = "rtsp://admin:Camerite@186.226.193.111:601/h264/ch1/main/av_stream"

print(f"Testando camera {CAMERA_ID}")
print(f"Conectando...")

cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("ERRO: Nao conectou ao RTSP")
    print("Verifique se a URL esta correta")
    exit(1)

print("Conectado! Processando...")

detections = 0
frame_count = 0

while detections < 5:
    ret, frame = cap.read()
    if not ret:
        print("Erro ao ler frame")
        break
    
    frame_count += 1
    if frame_count % 30 != 0:
        continue
    
    h, w = frame.shape[:2]
    crop = frame[h//4:3*h//4, w//4:3*w//4]
    
    _, buffer = cv2.imencode('.jpg', crop, [cv2.IMWRITE_JPEG_QUALITY, 85])
    
    files = {'image': ('det.jpg', buffer.tobytes(), 'image/jpeg')}
    data = {
        'camera_id': CAMERA_ID,
        'timestamp': datetime.now().isoformat(),
        'plate': f"TEST{np.random.randint(1000,9999)}",
        'confidence': 0.92,
        'vehicle_type': 'car'
    }
    
    response = requests.post(BACKEND_URL, data=data, files=files, headers={'X-API-Key': API_KEY}, timeout=5)
    
    if response.status_code == 201:
        detections += 1
        print(f"  Deteccao {detections}/5 enviada com sucesso!")
    else:
        print(f"  Erro: {response.status_code} - {response.text[:100]}")

cap.release()
print(f"\nConcluido! {detections} deteccoes enviadas")
print("Verifique em: backend/media/detections/")
