"""
Testa camera 2 - Captura direta do banco
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cameras.models import Camera
import cv2
import requests
from datetime import datetime
import numpy as np

BACKEND_URL = "http://backend:8000/api/ingest/"
API_KEY = "your-ingest-api-key-here"

# Busca camera 2
camera = Camera.objects.get(id=2)
print(f"Camera: {camera.name}")
print(f"RTSP: {camera.stream_url}")

cap = cv2.VideoCapture(camera.stream_url)

if not cap.isOpened():
    print("ERRO: Nao conectou")
    exit(1)

print("Conectado! Enviando 5 deteccoes...")

detections = 0
frame_count = 0

while detections < 5:
    ret, frame = cap.read()
    if not ret:
        print("Erro lendo frame")
        break
    
    frame_count += 1
    if frame_count % 30 != 0:
        continue
    
    h, w = frame.shape[:2]
    crop = frame[h//4:3*h//4, w//4:3*w//4]
    
    _, buffer = cv2.imencode('.jpg', crop, [cv2.IMWRITE_JPEG_QUALITY, 85])
    
    files = {'image': ('det.jpg', buffer.tobytes(), 'image/jpeg')}
    data = {
        'camera_id': 2,
        'timestamp': datetime.now().isoformat(),
        'plate': f"TEST{np.random.randint(1000,9999)}",
        'confidence': 0.90,
        'vehicle_type': 'car'
    }
    
    response = requests.post(BACKEND_URL, data=data, files=files, headers={'X-API-Key': API_KEY}, timeout=5)
    
    if response.status_code == 201:
        detections += 1
        print(f"  {detections}/5 OK")
    else:
        print(f"  Erro: {response.status_code}")

cap.release()
print(f"\nConcluido! {detections} deteccoes")
