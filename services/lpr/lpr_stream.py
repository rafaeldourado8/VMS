import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import cv2
import subprocess
import threading
import logging
import json
import uuid
from datetime import datetime
from pathlib import Path
import torch
from ultralytics import YOLO
from src.run_video_file_stream import predict_and_detect, validate_and_annotate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar modelo globalmente
model = YOLO(os.getcwd() + "/weights/license_plate_detector.pt")
model.fuse()

if torch.cuda.is_available():
    model.to("cuda")
    logger.info("Using CUDA for inference.")
else:
    logger.info("Using CPU for inference.")

class LPRStreamService:
    def __init__(self, camera_id, input_stream, output_rtsp, snapshot_dir="/app/snapshots"):
        self.camera_id = camera_id
        self.input_stream = input_stream
        self.output_rtsp = output_rtsp
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.running = False
        self.ffmpeg_process = None
        
    def start(self):
        self.running = True
        print(f"[START] Criando thread para câmera {self.camera_id}", flush=True)
        thread = threading.Thread(target=self._process, daemon=True)
        thread.start()
        print(f"[START] Thread iniciada para câmera {self.camera_id}", flush=True)
        
    def stop(self):
        self.running = False
        if self.ffmpeg_process:
            self.ffmpeg_process.stdin.close()
            self.ffmpeg_process.wait()
            
    def _process(self):
        print(f"[PROCESS] Thread _process iniciada para câmera {self.camera_id}", flush=True)
        try:
            print(f"[PROCESS] Abrindo stream: {self.input_stream}", flush=True)
            cap = cv2.VideoCapture(self.input_stream)
            print(f"[PROCESS] VideoCapture criado, testando isOpened()...", flush=True)
            is_opened = cap.isOpened()
            print(f"[PROCESS] isOpened() = {is_opened}", flush=True)
            if not is_opened:
                print(f"[PROCESS] Falha ao abrir {self.input_stream}", flush=True)
                return
            
            fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"[PROCESS] Stream aberto: {width}x{height} @ {fps}fps", flush=True)
            
            # FFmpeg desabilitado temporariamente para debug
            # print(f"[PROCESS] Iniciando FFmpeg para {self.output_rtsp}", flush=True)
            # self.ffmpeg_process = subprocess.Popen([
            #     'ffmpeg', '-y',
            #     '-f', 'rawvideo', '-vcodec', 'rawvideo', '-pix_fmt', 'bgr24',
            #     '-s', f'{width}x{height}', '-r', str(fps), '-i', '-',
            #     '-c:v', 'libx264', '-preset', 'ultrafast', '-tune', 'zerolatency',
            #     '-b:v', '2M', '-g', str(fps), '-f', 'rtsp', self.output_rtsp
            # ], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            
            frame_count = 0
            print(f"[PROCESS] Iniciando loop de processamento para câmera {self.camera_id}", flush=True)
            
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"Fim do stream para câmera {self.camera_id}")
                    break
                    
                frame_count += 1
                
                if frame_count % 30 == 0:
                    print(f"[PROCESS] Processando frame {frame_count} da câmera {self.camera_id}", flush=True)
                
                # Usa o código LPR original
                result_img, results = predict_and_detect(model, frame)
                annotated_img = validate_and_annotate(result_img, results)
                
                # Salva snapshot quando detectar veículos
                if results and len(results) > 0 and len(results[0].boxes) > 0:
                    print(f"[DETECT] Detectados {len(results[0].boxes)} veículos no frame {frame_count}", flush=True)
                    self._save_snapshot(annotated_img, results)
                
                # Envia para FFmpeg (desabilitado)
                # try:
                #     self.ffmpeg_process.stdin.write(annotated_img.tobytes())
                # except Exception as e:
                #     print(f"[ERROR] Erro ao enviar frame para FFmpeg: {e}", flush=True)
                #     break
                    
            cap.release()
            logger.info(f"Stream encerrado para câmera {self.camera_id}")
        except Exception as e:
            logger.error(f"Erro no processamento da câmera {self.camera_id}: {e}", exc_info=True)
        
    def _save_snapshot(self, frame, results):
        try:
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label = result.names[int(box.cls[0])]
                    conf = float(box.conf[0])
                    
                    uid = str(uuid.uuid4())[:8]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    det_dir = self.snapshot_dir / f"cam_{self.camera_id}" / f"{timestamp}_{uid}"
                    det_dir.mkdir(parents=True, exist_ok=True)
                    
                    vehicle_crop = frame[y1:y2, x1:x2]
                    vehicle_path = str(det_dir / "vehicle.jpg")
                    frame_path = str(det_dir / "full_frame.jpg")
                    
                    cv2.imwrite(vehicle_path, vehicle_crop)
                    cv2.imwrite(frame_path, frame)
                    
                    metadata = {
                        "uuid": uid,
                        "camera_id": self.camera_id,
                        "timestamp": datetime.now().isoformat(),
                        "vehicle_type": label,
                        "confidence": conf,
                        "bbox": [x1, y1, x2, y2]
                    }
                    
                    metadata_path = str(det_dir / "metadata.json")
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    print(f"[SNAPSHOT] Snapshot salvo: {det_dir}", flush=True)
        except Exception as e:
            print(f"[ERROR] Erro ao salvar snapshot: {e}", flush=True)

if __name__ == "__main__":
    service = LPRStreamService(
        camera_id=999,
        input_stream="/app/test_video.mp4",
        output_rtsp="rtsp://mediamtx:8554/test_ai"
    )
    service.start()
    
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()
