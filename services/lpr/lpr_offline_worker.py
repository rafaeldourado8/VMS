"""
LPR Offline Worker - Processa vídeos gravados
"""
import os
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
import httpx
import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
import asyncpg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lpr_offline")

class LPROfflineWorker:
    def __init__(self):
        self.storage_api = os.getenv("STORAGE_API_URL", "http://storage:8003")
        self.db_pool = None
        self.yolo_model = YOLO("weights/yolov8n.pt")
        self.ocr_reader = easyocr.Reader(['en'], gpu=True)
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def initialize(self):
        self.db_pool = await asyncpg.create_pool(
            host=os.getenv("POSTGRES_HOST", "postgres_main"),
            port=5432,
            user=os.getenv("POSTGRES_USER", "gtvision_user"),
            password=os.getenv("POSTGRES_PASSWORD", "your-secure-password-here"),
            database=os.getenv("POSTGRES_DB", "gtvision_db")
        )
        await self._create_tables()
        asyncio.create_task(self._process_loop())
    
    async def _create_tables(self):
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS lpr_events (
                    id SERIAL PRIMARY KEY,
                    camera_id INTEGER NOT NULL,
                    plate_number VARCHAR(20) NOT NULL,
                    confidence FLOAT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    recording_path TEXT,
                    frame_offset INTEGER,
                    bbox_json JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_lpr_camera_time ON lpr_events(camera_id, timestamp);
                CREATE INDEX IF NOT EXISTS idx_lpr_plate ON lpr_events(plate_number);
            """)
    
    async def _process_loop(self):
        """Loop principal: busca gravações não processadas"""
        while True:
            try:
                await asyncio.sleep(30)
                await self._process_pending_recordings()
            except Exception as e:
                logger.error(f"Erro no loop: {e}")
    
    async def _process_pending_recordings(self):
        """Busca e processa gravações pendentes"""
        # Busca últimas 2 horas de cada câmera
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=2)
        
        # Busca câmeras ativas
        cameras = await self._get_active_cameras()
        
        for camera_id in cameras:
            try:
                resp = await self.client.post(
                    f"{self.storage_api}/recordings/query",
                    json={
                        "camera_id": camera_id,
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat()
                    }
                )
                
                if resp.status_code == 200:
                    recordings = resp.json()
                    for rec in recordings:
                        if not rec["processed"]:
                            await self._process_recording(rec)
            except Exception as e:
                logger.error(f"Erro ao processar câmera {camera_id}: {e}")
    
    async def _get_active_cameras(self):
        """Busca IDs de câmeras ativas"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT id FROM cameras_camera WHERE status = 'online'")
            return [row["id"] for row in rows]
    
    async def _process_recording(self, recording: dict):
        """Processa um arquivo de gravação"""
        file_path = recording["path"]
        camera_id = recording["camera_id"]
        
        if not Path(file_path).exists():
            logger.warning(f"Arquivo não encontrado: {file_path}")
            return
        
        logger.info(f"Processando {file_path}")
        
        cap = cv2.VideoCapture(file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0
        
        # Processa 1 frame a cada 2 segundos
        skip_frames = int(fps * 2)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % skip_frames == 0:
                plates = await self._detect_plates(frame)
                
                for plate_data in plates:
                    timestamp = recording["start_time"] + timedelta(seconds=frame_count / fps)
                    await self._save_event(
                        camera_id=camera_id,
                        plate_number=plate_data["plate"],
                        confidence=plate_data["confidence"],
                        timestamp=timestamp,
                        recording_path=file_path,
                        frame_offset=frame_count,
                        bbox=plate_data["bbox"]
                    )
            
            frame_count += 1
        
        cap.release()
        
        # Marca como processado
        await self.client.post(
            f"{self.storage_api}/recordings/mark-processed",
            params={"file_path": file_path}
        )
        
        logger.info(f"Processamento concluído: {file_path}")
    
    async def _detect_plates(self, frame):
        """Detecta placas em um frame"""
        results = self.yolo_model(frame, classes=[2], conf=0.3)
        plates = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                
                plate_img = frame[y1:y2, x1:x2]
                
                ocr_results = self.ocr_reader.readtext(plate_img)
                
                for detection in ocr_results:
                    text = detection[1].upper().replace(" ", "")
                    ocr_conf = detection[2]
                    
                    if len(text) >= 6 and ocr_conf > 0.5:
                        plates.append({
                            "plate": text,
                            "confidence": (conf + ocr_conf) / 2,
                            "bbox": [x1, y1, x2, y2]
                        })
        
        return plates
    
    async def _save_event(self, camera_id, plate_number, confidence, timestamp, recording_path, frame_offset, bbox):
        """Salva evento LPR no banco"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO lpr_events 
                (camera_id, plate_number, confidence, timestamp, recording_path, frame_offset, bbox_json)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, camera_id, plate_number, confidence, timestamp, recording_path, frame_offset, bbox)

async def main():
    worker = LPROfflineWorker()
    await worker.initialize()
    
    # Mantém rodando
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
