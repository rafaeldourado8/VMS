import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import cv2
import json
import uuid
import threading
import re
import numpy as np
from datetime import datetime
from pathlib import Path
import torch
from ultralytics import YOLO

try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False

print("Carregando YOLO...", flush=True)
model = YOLO(os.getcwd() + "/weights/license_plate_detector.pt")
model.fuse()
if torch.cuda.is_available():
    model.to("cuda")

reader = None
if HAS_EASYOCR:
    print("Carregando EasyOCR...", flush=True)
    reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())
    print("OCR pronto", flush=True)

class LPRStreamService:
    def __init__(self, camera_id, input_stream, output_rtsp, snapshot_dir="/app/snapshots"):
        self.camera_id = camera_id
        self.input_stream = input_stream
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.preview_dir = Path("/app/snapshots/preview")
        self.preview_dir.mkdir(parents=True, exist_ok=True)
        self.running = False
        
        self.roi = None
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=False)
        self.tracked_plates = {}
        self.frame_count = 0
        
    def start(self):
        self.running = True
        print(f"[START] Câmera {self.camera_id}", flush=True)
        threading.Thread(target=self._process, daemon=True).start()
        
    def stop(self):
        self.running = False
    
    def _detect_roi(self, frame):
        fg_mask = self.bg_subtractor.apply(frame)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))
        
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            x_min, y_min = frame.shape[1], frame.shape[0]
            x_max, y_max = 0, 0
            
            for cnt in contours:
                if cv2.contourArea(cnt) > 500:
                    x, y, w, h = cv2.boundingRect(cnt)
                    x_min, y_min = min(x_min, x), min(y_min, y)
                    x_max, y_max = max(x_max, x+w), max(y_max, y+h)
            
            if x_max > x_min and y_max > y_min:
                margin_x = int((x_max - x_min) * 0.2)
                margin_y = int((y_max - y_min) * 0.2)
                x_min = max(0, x_min - margin_x)
                y_min = max(0, y_min - margin_y)
                x_max = min(frame.shape[1], x_max + margin_x)
                y_max = min(frame.shape[0], y_max + margin_y)
                return (x_min, y_min, x_max, y_max)
        return None
    
    def _get_plate_id(self, bbox):
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        return f"{center_x//50}_{center_y//50}"
    
    def _should_save(self, plate_id, bbox):
        if plate_id not in self.tracked_plates:
            self.tracked_plates[plate_id] = {'last_seen': self.frame_count, 'bbox': bbox, 'saved': False}
            return True
        
        track = self.tracked_plates[plate_id]
        if track['saved']:
            track['last_seen'] = self.frame_count
            return False
        
        if self.frame_count - track['last_seen'] >= 10:
            return True
        
        track['last_seen'] = self.frame_count
        return False
    
    def _cleanup_tracking(self):
        to_remove = [pid for pid, track in self.tracked_plates.items() 
                     if self.frame_count - track['last_seen'] > 60]
        for pid in to_remove:
            del self.tracked_plates[pid]
            
    def _process(self):
        print(f"[PROCESS] Iniciando câmera {self.camera_id}", flush=True)
        try:
            cap = cv2.VideoCapture(self.input_stream)
            if not cap.isOpened():
                return
            
            print(f"[PROCESS] Stream aberto", flush=True)
            
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                self.frame_count += 1
                
                # ROI desabilitado temporariamente para debug
                # if self.frame_count % 30 == 0:
                #     self.roi = self._detect_roi(frame)
                #     self._cleanup_tracking()
                
                process_frame = frame
                roi_offset = (0, 0)
                
                results = model.predict(process_frame, conf=0.3, verbose=False)
                
                # Debug: quantas detecções?
                if self.frame_count % 30 == 0:
                    num_detections = len(results[0].boxes) if results and len(results) > 0 else 0
                    print(f"[DEBUG] Frame {self.frame_count} - Detecções: {num_detections}", flush=True)
                
                annotated_frame = frame.copy()
                
                if self.roi:
                    cv2.rectangle(annotated_frame, (self.roi[0], self.roi[1]), 
                                (self.roi[2], self.roi[3]), (255, 255, 0), 2)
                
                if results and len(results) > 0 and len(results[0].boxes) > 0:
                    for box in results[0].boxes:
                        bbox_local = list(map(int, box.xyxy[0]))
                        bbox_global = [
                            bbox_local[0] + roi_offset[0],
                            bbox_local[1] + roi_offset[1],
                            bbox_local[2] + roi_offset[0],
                            bbox_local[3] + roi_offset[1]
                        ]
                        
                        plate_id = self._get_plate_id(bbox_global)
                        conf = float(box.conf[0])
                        
                        if plate_id in self.tracked_plates and self.tracked_plates[plate_id].get('saved'):
                            color = (0, 255, 0)
                            status = "SAVED"
                        elif plate_id in self.tracked_plates:
                            color = (0, 255, 255)
                            status = "TRACKING"
                        else:
                            color = (0, 0, 255)
                            status = "NEW"
                        
                        cv2.rectangle(annotated_frame, 
                                    (bbox_global[0], bbox_global[1]),
                                    (bbox_global[2], bbox_global[3]),
                                    color, 2)
                        
                        label = f"{status} {conf:.2f}"
                        if plate_id in self.tracked_plates and 'plate_text' in self.tracked_plates[plate_id]:
                            plate_text = self.tracked_plates[plate_id]['plate_text']
                            if plate_text:
                                label = f"{plate_text} {conf:.2f}"
                        
                        cv2.putText(annotated_frame, label,
                                  (bbox_global[0], bbox_global[1]-10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        
                        if self._should_save(plate_id, bbox_global):
                            plate_text = self._save_snapshot(frame, bbox_global, conf, plate_id)
                            if plate_text:
                                self.tracked_plates[plate_id]['plate_text'] = plate_text
                            self.tracked_plates[plate_id]['saved'] = True
                
                cv2.putText(annotated_frame, f"Cam {self.camera_id} | Frame {self.frame_count}",
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(annotated_frame, f"Tracked: {len(self.tracked_plates)}",
                          (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Salva frame anotado a cada 30 frames
                if self.frame_count % 30 == 0:
                    preview_path = self.preview_dir / f"cam_{self.camera_id}_preview.jpg"
                    cv2.imwrite(str(preview_path), annotated_frame)
                    
            cap.release()
            print(f"[PROCESS] Encerrado câmera {self.camera_id}", flush=True)
        except Exception as e:
            print(f"[ERROR] {e}", flush=True)
    
    def _validate_mercosul(self, text):
        """Valida padrão Mercosul: ABC1D23 (3 letras + 1 número + 1 letra + 2 números)"""
        if len(text) != 7:
            return None
        pattern = r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$'
        return text if re.match(pattern, text) else None
    
    def _extract_plate_text(self, plate_img):
        if reader is None:
            return None
        try:
            gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            
            # Tenta múltiplos pré-processamentos
            candidates = []
            
            # 1. Threshold adaptativo
            thresh1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                           cv2.THRESH_BINARY, 11, 2)
            result1 = reader.readtext(thresh1, detail=1, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            for (_, text, conf) in result1:
                if conf > 0.4:
                    clean = re.sub(r'[^A-Z0-9]', '', text.upper())
                    validated = self._validate_mercosul(clean)
                    if validated:
                        candidates.append((validated, conf))
            
            # 2. OTSU threshold
            _, thresh2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            result2 = reader.readtext(thresh2, detail=1, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            for (_, text, conf) in result2:
                if conf > 0.4:
                    clean = re.sub(r'[^A-Z0-9]', '', text.upper())
                    validated = self._validate_mercosul(clean)
                    if validated:
                        candidates.append((validated, conf))
            
            # Retorna candidato com maior confiança
            if candidates:
                candidates.sort(key=lambda x: x[1], reverse=True)
                return candidates[0][0]
            
            return None
        except:
            return None
    
    def _save_snapshot(self, frame, bbox, conf, plate_id):
        try:
            x1, y1, x2, y2 = bbox
            plate_crop = frame[y1:y2, x1:x2]
            if plate_crop.size == 0:
                return None
            
            plate_text = self._extract_plate_text(plate_crop)
            if not plate_text and reader is not None:
                return None
            
            uid = str(uuid.uuid4())[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            det_dir = self.snapshot_dir / f"cam_{self.camera_id}" / f"{timestamp}_{uid}"
            det_dir.mkdir(parents=True, exist_ok=True)
            
            cv2.imwrite(str(det_dir / "plate.jpg"), plate_crop)
            cv2.imwrite(str(det_dir / "full_frame.jpg"), frame)
            
            # Valida Mercosul
            is_mercosul = self._validate_mercosul(plate_text) if plate_text else False
            
            metadata = {
                "uuid": uid,
                "camera_id": self.camera_id,
                "timestamp": datetime.now().isoformat(),
                "plate_text": plate_text,
                "confidence": conf,
                "bbox": bbox,
                "plate_id": plate_id,
                "is_mercosul": is_mercosul,
                "ocr_available": reader is not None
            }
            
            with open(det_dir / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Envia para backend
            self._send_to_backend(metadata, det_dir)
            
            if plate_text:
                mercosul_tag = " [MERCOSUL]" if is_mercosul else ""
                print(f"[SAVED] Placa: {plate_text}{mercosul_tag} (conf: {conf:.2f})", flush=True)
            else:
                print(f"[SAVED] Sem OCR (conf: {conf:.2f})", flush=True)
            
            return plate_text
        except Exception as e:
            print(f"[ERROR] Save: {e}", flush=True)
            return None
    
    def _send_to_backend(self, metadata, det_dir):
        """Envia detecção para backend Django"""
        try:
            import httpx
            payload = {
                "camera_id": metadata["camera_id"],
                "plate_text": metadata["plate_text"],
                "confidence": metadata["confidence"],
                "bbox": metadata["bbox"],
                "plate_id": metadata["plate_id"],
                "is_mercosul": metadata["is_mercosul"],
                "plate_image_path": f"cam_{self.camera_id}/{det_dir.name}/plate.jpg",
                "full_frame_path": f"cam_{self.camera_id}/{det_dir.name}/full_frame.jpg",
                "metadata": metadata
            }
            
            httpx.post(
                "http://backend:8000/api/deteccoes/lpr/ingest/",
                json=payload,
                timeout=5.0
            )
        except:
            pass  # Falha silenciosa
