import asyncio
import logging
import cv2
import os
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO
import easyocr

logger = logging.getLogger(__name__)

class LPROfflineProcessor:
    """Processa LPR em vídeos gravados (não em tempo real)."""
    
    def __init__(self, recordings_path: str = "/recordings"):
        self.recordings_path = Path(recordings_path)
        self.detector = YOLO("/app/weights/license_plate_detector.pt")
        self.reader = easyocr.Reader(['en'], gpu=True)
    
    async def process_recording(self, recording_id: int):
        """Processa um vídeo gravado para detecção de placas."""
        from apps.cameras.models_recording import Recording
        from apps.deteccoes.models import Deteccao
        
        try:
            recording = await Recording.objects.select_related('camera').aget(id=recording_id)
            
            if recording.lpr_processed:
                logger.info(f"Recording {recording_id} já processado")
                return
            
            recording.lpr_processing_started_at = datetime.now()
            await recording.asave()
            
            video_path = self.recordings_path / recording.video_path.lstrip('/')
            if not video_path.exists():
                logger.error(f"Vídeo não encontrado: {video_path}")
                return
            
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_skip = int(fps * 2)  # Processa 1 frame a cada 2 segundos
            frame_count = 0
            detections_count = 0
            
            logger.info(f"🎬 Processando {video_path} (FPS: {fps}, skip: {frame_skip})")
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                if frame_count % frame_skip != 0:
                    continue
                
                # Detecta placas
                results = self.detector(frame, conf=0.5, verbose=False)
                
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        plate_img = frame[y1:y2, x1:x2]
                        
                        # OCR
                        ocr_results = self.reader.readtext(plate_img)
                        if ocr_results:
                            text = ocr_results[0][1]
                            conf = ocr_results[0][2]
                            
                            # Salva snapshot
                            snapshot_dir = Path("/app/media/snapshots") / datetime.now().strftime("%Y/%m/%d")
                            snapshot_dir.mkdir(parents=True, exist_ok=True)
                            snapshot_path = snapshot_dir / f"{recording_id}_{frame_count}_{text}.jpg"
                            cv2.imwrite(str(snapshot_path), plate_img)
                            
                            # Cria detecção
                            await Deteccao.objects.acreate(
                                camera=recording.camera,
                                placa=text,
                                confianca=conf,
                                snapshot_path=str(snapshot_path.relative_to("/app/media")),
                                data_hora=recording.started_at
                            )
                            detections_count += 1
            
            cap.release()
            
            # Atualiza recording
            recording.lpr_processed = True
            recording.lpr_detections_count = detections_count
            await recording.asave()
            
            logger.info(f"✅ Recording {recording_id} processado: {detections_count} detecções")
        
        except Exception as e:
            logger.error(f"Erro ao processar recording {recording_id}: {e}")
    
    async def run_worker(self):
        """Worker que processa gravações pendentes."""
        from apps.cameras.models_recording import Recording
        
        while True:
            try:
                # Busca gravações não processadas
                recordings = Recording.objects.filter(
                    lpr_processed=False,
                    ended_at__isnull=False  # Só processa gravações finalizadas
                ).order_by('created_at')[:5]
                
                async for recording in recordings:
                    await self.process_recording(recording.id)
                
                await asyncio.sleep(30)  # Verifica a cada 30s
            except Exception as e:
                logger.error(f"Erro no worker: {e}")
                await asyncio.sleep(60)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    processor = LPROfflineProcessor()
    asyncio.run(processor.run_worker())
