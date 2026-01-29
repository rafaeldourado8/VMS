import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import cv2
import json
import uuid
import threading
import re
from datetime import datetime
from pathlib import Path
import torch
from ultralytics import YOLO
from paddleocr import PaddleOCR

print("Carregando modelo YOLO...", flush=True)
model = YOLO(os.getcwd() + "/weights/license_plate_detector.pt")
model.fuse()

if torch.cuda.is_available():
    model.to("cuda")
    print("Using CUDA", flush=True)
else:
    print("Using CPU", flush=True)

print("Inicializando PaddleOCR...", flush=True)
try:
    ocr = PaddleOCR(use_angle_cls=False, lang="en", use_gpu=True if torch.cuda.is_available() else False)
    print("OCR pronto", flush=True)
except Exception as e:
    print(f"Erro ao inicializar OCR: {e}", flush=True)
    ocr = None

class LPRStreamService:
    def __init__(self, camera_id, input_stream, output_rtsp, snapshot_dir="/app/snapshots"):
        self.camera_id = camera_id
        self.input_stream = input_stream
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.running = False
        
    def start(self):
        self.running = True
        print(f"[START] Thread para câmera {self.camera_id}", flush=True)
        thread = threading.Thread(target=self._process, daemon=True)
        thread.start()
        
    def stop(self):
        self.running = False
            
    def _process(self):
        print(f"[PROCESS] Iniciada câmera {self.camera_id}", flush=True)
        try:
            cap = cv2.VideoCapture(self.input_stream)
            if not cap.isOpened():
                print(f"[ERROR] Falha ao abrir {self.input_stream}", flush=True)
                return
            
            fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"[PROCESS] Stream: {width}x{height} @ {fps}fps", flush=True)
            
            frame_count = 0
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    print(f"[PROCESS] Fim do stream", flush=True)
                    break
                    
                frame_count += 1
                
                if frame_count % 30 == 0:
                    print(f"[PROCESS] Frame {frame_count}", flush=True)
                
                # Detecção simples
                results = model.predict(frame, conf=0.4, verbose=False)
                
                # Salva snapshot quando detectar
                if results and len(results) > 0 and len(results[0].boxes) > 0:
                    print(f"[DETECT] {len(results[0].boxes)} objetos no frame {frame_count}", flush=True)
                    self._save_snapshot(frame, results)
                    
            cap.release()
            print(f"[PROCESS] Encerrado câmera {self.camera_id}", flush=True)
        except Exception as e:
            print(f"[ERROR] {e}", flush=True)
        
    def _save_snapshot(self, frame, results):
        try:
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label = result.names[int(box.cls[0])]
                    conf = float(box.conf[0])
                    
                    # Extrair texto da placa se for License_Plate
                    plate_text = None
                    if label == "License_Plate":
                        plate_crop = frame[y1:y2, x1:x2]
                        plate_text = self._extract_plate_text(plate_crop)
                    
                    uid = str(uuid.uuid4())[:8]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    det_dir = self.snapshot_dir / f"cam_{self.camera_id}" / f"{timestamp}_{uid}"
                    det_dir.mkdir(parents=True, exist_ok=True)
                    
                    vehicle_crop = frame[y1:y2, x1:x2]
                    cv2.imwrite(str(det_dir / "vehicle.jpg"), vehicle_crop)
                    cv2.imwrite(str(det_dir / "full_frame.jpg"), frame)
                    
                    if label == "License_Plate":
                        cv2.imwrite(str(det_dir / "plate.jpg"), vehicle_crop)
                    
                    metadata = {
                        "uuid": uid,
                        "camera_id": self.camera_id,
                        "timestamp": datetime.now().isoformat(),
                        "vehicle_type": label,
                        "confidence": conf,
                        "bbox": [x1, y1, x2, y2],
                        "plate_text": plate_text
                    }
                    
                    with open(det_dir / "metadata.json", 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    if plate_text:
                        print(f"[SNAPSHOT] Placa: {plate_text} - {det_dir}", flush=True)
                    else:
                        print(f"[SNAPSHOT] Salvo: {det_dir}", flush=True)
        except Exception as e:
            print(f"[ERROR] Snapshot: {e}", flush=True)
    
    def _extract_plate_text(self, plate_img):
        if ocr is None:
            return None
        try:
            # Redimensionar para melhorar OCR
            h, w = plate_img.shape[:2]
            if h < 32:
                scale = 32 / h
                plate_img = cv2.resize(plate_img, (int(w * scale), 32))
            
            result = ocr.ocr(plate_img)
            if not result or not result[0]:
                return None
            
            texts = []
            for line in result[0]:
                if len(line) >= 2 and isinstance(line[1], tuple):
                    text, conf = line[1]
                    if conf > 0.5:
                        clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())
                        if clean_text:
                            texts.append(clean_text)
            
            plate_text = ''.join(texts)
            if plate_text:
                print(f"[OCR] Texto extraído: {plate_text} (conf: {conf:.2f})", flush=True)
            return plate_text if plate_text else None
        except Exception as e:
            print(f"[ERROR] OCR: {e}", flush=True)
            return None
