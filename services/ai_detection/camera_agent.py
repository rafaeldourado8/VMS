import threading
import time
import cv2
import base64
import requests
import logging
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class CameraAgent:
    def __init__(self, camera_id, rtsp_url, model_yolo, model_ocr, backend_url):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.yolo = model_yolo
        self.ocr = model_ocr
        self.backend_url = backend_url
        
        self.running = False
        self.latest_frame = None
        self.lock = threading.Lock()
        
        # Debounce: Evita enviar a mesma placa repetidamente (5 segundos)
        self.last_plate = None
        self.last_detection_time = 0
        self.debounce_seconds = 5.0

    def start(self):
        self.running = True
        # Thread 1: Leitura de Vídeo (Alta prioridade, limpa buffer)
        threading.Thread(target=self._read_stream, daemon=True).start()
        # Thread 2: Inteligência Artificial (Processamento assíncrono)
        threading.Thread(target=self._process_ai, daemon=True).start()

    def stop(self):
        self.running = False

    def _read_stream(self):
        logger.info(f"[{self.camera_id}] Conectando ao RTSP: {self.rtsp_url}")
        cap = cv2.VideoCapture(self.rtsp_url)
        # Força buffer zero/um para latência mínima
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        while self.running:
            ret, frame = cap.read()
            if not ret:
                logger.warning(f"[{self.camera_id}] Falha no stream. Reconectando em 5s...")
                cap.release()
                time.sleep(5)
                cap = cv2.VideoCapture(self.rtsp_url)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                continue
            
            # Atualiza o frame de forma thread-safe
            with self.lock:
                self.latest_frame = frame
            
            # Pequena pausa para ceder CPU
            time.sleep(0.001)
        
        cap.release()

    def _process_ai(self):
        logger.info(f"[{self.camera_id}] IA Iniciada.")
        
        while self.running:
            frame = None
            with self.lock:
                if self.latest_frame is not None:
                    frame = self.latest_frame.copy()
            
            if frame is None:
                time.sleep(0.1)
                continue

            try:
                # 1. Detecção YOLO (Carros/Placas)
                results = self.yolo(frame, verbose=False, conf=0.7)  # Mínimo 70%
                
                for result in results:
                    for box in result.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        confidence = float(box.conf[0])
                        
                        # Recorte da placa (com margem de segurança se possível)
                        h, w, _ = frame.shape
                        p_x1 = max(0, x1 - 5)
                        p_y1 = max(0, y1 - 5)
                        p_x2 = min(w, x2 + 5)
                        p_y2 = min(h, y2 + 5)
                        
                        plate_crop = frame[p_y1:p_y2, p_x1:p_x2]
                        
                        # 2. OCR (Leitura)
                        # A lib espera uma lista de imagens
                        ocr_res = self.ocr.run([plate_crop])
                        if ocr_res:
                            plate_text = ocr_res[0]
                            
                            # Filtro básico de formato de placa
                            if plate_text and len(plate_text) >= 5:
                                self._handle_detection(plate_text, plate_crop, confidence)
                                
            except Exception as e:
                logger.error(f"[{self.camera_id}] Erro no pipeline de IA: {e}")
            
            # Limita a taxa de inferência para não fritar a CPU (max 5 FPS)
            time.sleep(0.2)

    def _handle_detection(self, plate, image, confidence):
        now = time.time()
        
        # Lógica de Debounce
        if plate == self.last_plate and (now - self.last_detection_time) < self.debounce_seconds:
            return

        logger.info(f" [{self.camera_id}] NOVA PLACA: {plate} ({confidence:.2f})")
        self.last_plate = plate
        self.last_detection_time = now
        
        self._send_to_backend(plate, image, confidence)

    def _send_to_backend(self, plate, image, confidence):
        if not self.backend_url:
            return

        try:
            # Converte imagem para Base64 para envio JSON
            _, buffer = cv2.imencode('.jpg', image)
            img_b64 = base64.b64encode(buffer).decode('utf-8')
            
            payload = {
                "camera_id": self.camera_id,
                "plate_number": plate,
                "confidence": confidence,
                "image_base64": img_b64,
                "timestamp": datetime.now().isoformat()
            }
            
            headers = {'Content-Type': 'application/json'}
            # Endpoint específico para ingestão rápida
            url = f"{self.backend_url}/api/deteccoes/fast_ingest/"
            
            requests.post(url, json=payload, headers=headers, timeout=2)
            
        except Exception as e:
            logger.error(f"[{self.camera_id}] Erro ao enviar para API: {e}")