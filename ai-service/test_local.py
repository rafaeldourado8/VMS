"""
Teste local sem Docker - instale as dependências primeiro:
pip install opencv-python ultralytics torch torchvision numpy pillow
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time

CAMERAS = [
    {"id": 1, "url": "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0"},
    {"id": 2, "url": "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0"},
    {"id": 3, "url": "rtsp://admin:Camerite123@45.236.226.74:6050/cam/realmonitor?channel=1&subtype=0"},
    {"id": 4, "url": "rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0"},
]

print("Carregando modelo YOLO...")
model = YOLO("models/yolov8n.pt")
print("✅ Modelo carregado\n")

for camera in CAMERAS:
    print(f"{'='*60}")
    print(f"Testando Câmera {camera['id']}")
    print(f"{'='*60}")
    
    cap = cv2.VideoCapture(camera['url'])
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print(f"❌ Erro ao capturar frame\n")
        continue
    
    h, w = frame.shape[:2]
    print(f"✅ Frame capturado: {w}x{h}")
    
    start = time.time()
    results = model(frame, conf=0.5, classes=[2, 3, 5, 7], verbose=False)
    elapsed = (time.time() - start) * 1000
    
    print(f"⏱️  Tempo de detecção: {elapsed:.2f}ms")
    
    detections = []
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            
            class_names = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
            obj_type = class_names.get(cls, "vehicle")
            
            detections.append({
                "type": obj_type,
                "confidence": conf,
                "bbox": (x1, y1, x2-x1, y2-y1)
            })
    
    print(f"🔍 Detecções: {len(detections)}")
    
    if detections:
        for i, det in enumerate(detections, 1):
            print(f"  [{i}] {det['type'].upper()} - {det['confidence']:.2%}")
            print(f"      BBox: x={det['bbox'][0]}, y={det['bbox'][1]}, w={det['bbox'][2]}, h={det['bbox'][3]}")
    else:
        print("  Nenhum veículo detectado")
    
    print()
    time.sleep(2)

print(f"{'='*60}")
print("TESTE CONCLUÍDO")
print(f"{'='*60}")
