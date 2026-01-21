import threading
import time
import cv2
import base64
import requests
import logging
import queue
import os
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class CameraAgent:
    def __init__(self, camera_id, rtsp_url, vehicle_model, custom_model, plate_model, ocr_model, backend_url, rabbitmq_producer=None):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        
        # --- OS 3 YOLOS (TRIPLE-CORE) + OCR ---
        self.vehicle_model = vehicle_model
        self.custom_model = custom_model
        self.plate_model = plate_model
        self.ocr = ocr_model
        
        # --- INFRA ---
        self.backend_url = backend_url
        self.rabbitmq_producer = rabbitmq_producer
        
        self.running = False
        self.lock = threading.Lock()
        
        # --- FILA DE PROCESSAMENTO ---
        # Reduzi para 20 para evitar consumo excessivo de RAM se a CPU engasgar
        self.process_queue = queue.Queue(maxsize=20) 
        
        # --- DETECTOR DE MOVIMENTO ---
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=25, detectShadows=False)
        self.min_motion_area = 2000
        
        # Debounce por placa
        self.last_detections = {}  # {plate: timestamp}
        self.debounce_seconds = 2.0

    def start(self):
        self.running = True
        threading.Thread(target=self._motion_monitor_loop, daemon=True).start()
        threading.Thread(target=self._ai_worker_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _motion_monitor_loop(self):
        logger.info(f"[{self.camera_id}] Monitor de Movimento Iniciado (Forçando TCP)")
        
        # [CORREÇÃO] Forçar FFMPEG a usar TCP para evitar perda de pacotes H264
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

        while self.running:
            cap = cv2.VideoCapture(self.rtsp_url)
            # Tenta usar API FFMPEG explicitamente se possível, senão vai no auto
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if not cap.isOpened():
                time.sleep(3)
                continue
            
            logger.info(f"[{self.camera_id}] Stream Conectado via TCP!")

            while self.running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"[{self.camera_id}] Frame corrompido ou fim de stream.")
                    break

                try:
                    # 1. Detecção de Movimento
                    mask = self.bg_subtractor.apply(frame)
                    _, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
                    motion_pixels = cv2.countNonZero(mask)
                    
                    # 2. Se tiver movimento, manda para a IA
                    if motion_pixels > self.min_motion_area:
                        if not self.process_queue.full():
                            self.process_queue.put(frame.copy())
                    
                    # Controle de FPS de LEITURA (30 FPS max)
                    time.sleep(0.01)
                    
                except Exception as e:
                    logger.error(f"[{self.camera_id}] Erro no loop de vídeo: {e}")
                    break

            cap.release()
            logger.warning(f"[{self.camera_id}] Conexão caiu. Reiniciando em 2s...")
            time.sleep(2)

    def _ai_worker_loop(self):
        logger.info(f"[{self.camera_id}] IA Triple-Core Pronta")
        
        while self.running:
            try:
                # Timeout curto para verificar se 'running' mudou
                frame = self.process_queue.get(timeout=1)
            except queue.Empty:
                continue 
            
            try:
                self._run_triple_core_pipeline(frame)
            except Exception as e:
                logger.error(f"[{self.camera_id}] Erro Pipeline IA: {e}")
            
            self.process_queue.task_done()

    def _run_triple_core_pipeline(self, frame):
        candidate_boxes = []

        # --- IA 1: CUSTOMIZADO ---
        # Aumentei um pouco a confiança para 0.45 para evitar falsos positivos de "fantasmas" no vídeo corrompido
        results_custom = self.custom_model(frame, verbose=False, conf=0.45)
        for res in results_custom:
            for box in res.boxes:
                candidate_boxes.append(box)

        # --- IA 2: VEÍCULOS PADRÃO ---
        results_vehicle = self.vehicle_model(frame, verbose=False, conf=0.45)
        for res in results_vehicle:
            for box in res.boxes:
                if int(box.cls[0]) in [2, 3, 5, 7]: 
                    candidate_boxes.append(box)

        # --- IA 3: PLACAS ---
        for box in candidate_boxes:
            self._inspect_candidate(frame, box)

    def _inspect_candidate(self, frame, box):
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        h, w, _ = frame.shape
        
        # Margem segura
        p_x1, p_y1 = max(0, x1 - 10), max(0, y1 - 10)
        p_x2, p_y2 = min(w, x2 + 10), min(h, y2 + 10)
        
        vehicle_crop = frame[p_y1:p_y2, p_x1:p_x2]
        if vehicle_crop.size == 0: return

        plate_results = self.plate_model(vehicle_crop, verbose=False, conf=0.3)
        
        for res in plate_results:
            for p_box in res.boxes:
                px1, py1, px2, py2 = map(int, p_box.xyxy[0])
                plate_img = vehicle_crop[py1:py2, px1:px2]
                
                if plate_img.size > 0:
                    combined_conf = (float(box.conf[0]) + float(p_box.conf[0])) / 2
                    self._run_ocr(plate_img, frame, combined_conf)

    def _run_ocr(self, plate_img, original_frame, confidence):
        # Threshold mais baixo para não perder detecções
        if confidence < 0.5:
            return
            
        ocr_res = self.ocr.run([plate_img])
        
        if ocr_res and len(ocr_res) > 0:
            text = ocr_res[0]
            clean_text = "".join([c for c in text if c.isalnum()]).upper()
            
            # Validação: Padrão brasileiro
            if self._is_valid_brazilian_plate(clean_text):
                self._handle_detection(clean_text, original_frame, confidence)
    
    def _is_valid_brazilian_plate(self, plate):
        """Valida se placa segue padrão brasileiro"""
        import re
        
        plate = plate.strip()
        
        if len(plate) != 7:
            return False
        
        # Mercosul: ABC1D23
        mercosul = re.match(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$', plate)
        
        # Antiga: ABC1234
        antiga = re.match(r'^[A-Z]{3}[0-9]{4}$', plate)
        
        # Aceita se for Mercosul ou Antiga
        if mercosul or antiga:
            # Validação adicional: não pode ter letras repetidas demais
            if plate[:3] == plate[0] * 3:  # AAA
                return False
            return True
        
        return False

    def _handle_detection(self, plate, image, confidence):
        now = time.time()
        
        # Verifica debounce apenas para esta placa específica
        if plate in self.last_detections:
            if (now - self.last_detections[plate]) < self.debounce_seconds:
                return
        
        logger.info(f"[{self.camera_id}] DETECCAO: {plate} ({confidence:.2f})")
        self.last_detections[plate] = now
        
        # Limpa detecções antigas (mais de 10 segundos)
        self.last_detections = {p: t for p, t in self.last_detections.items() if now - t < 10}
        
        _, buffer = cv2.imencode('.jpg', image)
        image_b64 = base64.b64encode(buffer).decode('utf-8')
        
        if self.rabbitmq_producer:
            self.rabbitmq_producer.send_detection(self.camera_id, plate, confidence, "motion_triple_core", image_base64=image_b64)
        
        threading.Thread(target=self._send_http, args=(plate, image, confidence)).start()

    def _send_http(self, plate, image, confidence):
        if not self.backend_url: return
        try:
            _, buffer = cv2.imencode('.jpg', image)
            b64 = base64.b64encode(buffer).decode('utf-8')
            requests.post(f"{self.backend_url}/api/deteccoes/fast_ingest/", json={
                "camera_id": self.camera_id, "plate_number": plate, 
                "confidence": confidence, "image_base64": b64, 
                "timestamp": datetime.now().isoformat()
            }, timeout=2)
        except: pass