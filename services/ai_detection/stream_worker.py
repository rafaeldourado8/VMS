"""
Stream Worker - Captura frames do HLS e processa com YOLO
"""
import asyncio
import cv2
import logging
import requests
from typing import Dict
from frame_processor import frame_processor

logger = logging.getLogger(__name__)

class StreamWorker:
    def __init__(self):
        self.active_streams: Dict[int, asyncio.Task] = {}
        self.running = False
    
    async def start(self):
        """Inicia o worker"""
        self.running = True
        logger.info("🚀 Stream Worker iniciado")
    
    async def stop(self):
        """Para o worker"""
        self.running = False
        for task in self.active_streams.values():
            task.cancel()
        self.active_streams.clear()
        logger.info("🛑 Stream Worker parado")
    
    async def add_camera(self, camera_id: int, stream_url: str):
        """Adiciona câmera para processamento"""
        if camera_id in self.active_streams:
            logger.warning(f"Câmera {camera_id} já está sendo processada")
            return
        
        task = asyncio.create_task(self._process_camera_stream(camera_id, stream_url))
        self.active_streams[camera_id] = task
        logger.info(f"📹 Câmera {camera_id} adicionada ao processamento")
    
    async def remove_camera(self, camera_id: int):
        """Remove câmera do processamento"""
        if camera_id in self.active_streams:
            self.active_streams[camera_id].cancel()
            del self.active_streams[camera_id]
            frame_processor.stop_camera(camera_id)
            logger.info(f"🛑 Câmera {camera_id} removida do processamento")
    
    async def _process_camera_stream(self, camera_id: int, stream_url: str):
        """Processa stream de uma câmera"""
        retry_count = 0
        max_retries = 5
        
        while self.running and retry_count < max_retries:
            try:
                # Tenta conectar ao stream
                cap = cv2.VideoCapture(stream_url)
                
                if not cap.isOpened():
                    logger.error(f"❌ Não foi possível abrir stream da câmera {camera_id}")
                    retry_count += 1
                    await asyncio.sleep(5)
                    continue
                
                logger.info(f"✅ Stream da câmera {camera_id} conectado")
                retry_count = 0
                frame_count = 0
                
                while self.running:
                    ret, frame = cap.read()
                    
                    if not ret:
                        logger.warning(f"⚠️ Falha ao ler frame da câmera {camera_id}")
                        break
                    
                    frame_count += 1
                    
                    # Processa a cada 30 frames (1 por segundo em 30fps)
                    if frame_count % 30 == 0:
                        detections = frame_processor.process_frame(camera_id, frame)
                        if detections:
                            logger.info(f"🚗 Câmera {camera_id}: {len(detections)} veículos detectados")
                    
                    # Pequeno delay para não sobrecarregar
                    await asyncio.sleep(0.01)
                
                cap.release()
                
            except Exception as e:
                logger.error(f"❌ Erro processando stream da câmera {camera_id}: {e}")
                retry_count += 1
                await asyncio.sleep(5)
        
        logger.warning(f"⚠️ Processamento da câmera {camera_id} encerrado")

# Instância global
stream_worker = StreamWorker()
