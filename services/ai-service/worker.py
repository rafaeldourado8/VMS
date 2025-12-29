import asyncio
import cv2
import numpy as np
import logging
import time
from typing import Optional, Dict
from detector import VehicleDetector
from motion_detector import MotionDetector
from queue_manager import QueueManager
from api_client import APIClient
from prometheus_client import Counter, Histogram, Gauge
from config import settings

logger = logging.getLogger(__name__)

# Métricas Prometheus para monitoramento
processed_counter = Counter('detections_processed_total', 'Total de detecções processadas')
processing_time = Histogram('detection_processing_seconds', 'Tempo gasto no processamento')
queue_size_gauge = Gauge('detection_queue_size', 'Tamanho atual da fila Redis')
motion_detection_gauge = Gauge('motion_detected', 'Status de detecção de movimento (0/1)')
rtsp_active_gauge = Gauge('rtsp_streams_active', 'Número de streams RTSP ativos')

class DetectionWorker:
    """
    Worker assíncrono para o Modo Task (Fila Redis).
    Processa imagens individuais enviadas pelo backend ou triggers externos.
    """
    
    def __init__(self, worker_id: int = 0):
        self.worker_id = worker_id
        self.detector = VehicleDetector()
        self.queue = QueueManager()
        self.api_client = APIClient()
        self.running = False
        
        self.stats = {
            "processed": 0,
            "total_time": 0.0,
            "errors": 0,
            "plates_detected": 0
        }
        
        logger.info(f"Worker {worker_id} inicializado")
    
    async def start(self):
        """Inicia o consumo da fila Redis."""
        await self.queue.connect()
        await self.api_client._ensure_session()
        
        self.running = True
        logger.info(f"Worker {self.worker_id} iniciado (Modo Task)")
        
        while self.running:
            try:
                task = await self.queue.dequeue()
                if task:
                    await self._process_task(task)
                
                queue_size = await self.queue.get_queue_size()
                queue_size_gauge.set(queue_size)
                
            except Exception as e:
                logger.error(f"Erro no Worker {self.worker_id}: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(1)
    
    async def stop(self):
        """Finaliza o worker com segurança."""
        self.running = False
        await self.queue.disconnect()
        await self.api_client.close()
        logger.info(f"Worker {self.worker_id} parado")
    
    async def _process_task(self, task: dict):
        """Decodifica a imagem e executa a inferência de IA."""
        start = time.time()
        
        try:
            # Decodifica imagem recebida via Redis
            image_bytes = bytes.fromhex(task["image_data"])
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Falha ao decodificar imagem")
            
            camera_id = task["camera_id"]
            # Executa detecção (YOLO + LPR)
            detections = self.detector.detect(image, camera_id)
            
            for detection in detections:
                if detection.get("plate_number"):
                    plate = detection["plate_number"]
                    self.stats["plates_detected"] += 1
                    
                    # Salva frame para futuro treinamento (AI-Processor legacy feature)
                    self.detector.save_for_training(image, plate)
                    
                    # Envia avistamento para o Django (Mapeado para IngestDeteccaoSerializer)
                    asyncio.create_task(
                        self.api_client.send_sighting(
                            plate=plate,
                            camera_id=camera_id,
                            vehicle_type=detection.get("object_type", "unknown"),
                            confidence=detection.get("plate_confidence", 0.0),
                            image_url=detection.get("image_path") # Caminho do crop salvo
                        )
                    )
            
            processing_time_ms = (time.time() - start) * 1000
            
            # Armazena o resultado no Redis para o endpoint síncrono
            result = {
                "camera_id": camera_id,
                "detections": detections,
                "processing_time_ms": processing_time_ms
            }
            await self.queue.store_result(task["task_id"], result)
            
            self.stats["processed"] += 1
            self.stats["total_time"] += processing_time_ms
            processed_counter.inc()
            processing_time.observe(time.time() - start)
            
        except Exception as e:
            logger.error(f"Erro no processamento da task {task.get('task_id')}: {e}")
            self.stats["errors"] += 1

    def get_stats(self) -> dict:
        avg = self.stats["total_time"] / self.stats["processed"] if self.stats["processed"] > 0 else 0
        return {**self.stats, "avg_processing_time_ms": round(avg, 2)}


class StreamWorker:
    """
    Worker para Modo Stream (RTSP Contínuo).
    Otimizado com Motion Detection para evitar processamento inútil em cenas estáticas.
    """
    
    def __init__(self, camera_info: dict):
        self.camera_info = camera_info
        self.camera_id = camera_info["id"]
        self.camera_name = camera_info.get("name", f"Cam {self.camera_id}")
        self.rtsp_url = camera_info["rtsp_url"]
        
        self.detector = VehicleDetector()
        self.motion_detector = MotionDetector()
        self.api_client = APIClient()
        
        self.running = False
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame_count = 0
    
    async def start(self):
        """Inicia a captura RTSP (Preferencialmente via TCP/MediaMTX)."""
        await self.api_client._ensure_session()
        self.running = True
        rtsp_active_gauge.inc()
        logger.info(f"StreamWorker iniciado: {self.camera_name}")
        await self._process_stream()
    
    async def stop(self):
        self.running = False
        if self.cap: self.cap.release()
        await self.api_client.close()
        rtsp_active_gauge.dec()
        logger.info(f"StreamWorker parado: {self.camera_name}")
    
    async def _process_stream(self):
        """Loop principal com Gatilho de Movimento."""
        while self.running:
            try:
                if not self.cap or not self.cap.isOpened():
                    # Abre conexão RTSP (Forçar TCP no URL ou config é recomendado)
                    self.cap = cv2.VideoCapture(self.rtsp_url)
                    if not self.cap.isOpened():
                        await asyncio.sleep(settings.rtsp_reconnect_delay)
                        continue
                    self.motion_detector.reset()
                
                ret, frame = self.cap.read()
                if not ret:
                    self.cap.release()
                    await asyncio.sleep(2)
                    continue
                
                self.frame_count += 1
                # Otimização: Pula frames conforme configuração (ex: processa 1 a cada 5)
                if self.frame_count % settings.rtsp_frame_skip != 0:
                    continue
                
                # PASSO 1: Gatilho de Movimento (Muito leve - CPU)
                motion_detected, _ = self.motion_detector.detect(frame)
                motion_detection_gauge.set(1 if motion_detected else 0)
                
                # PASSO 2: Inferência IA (Pesado - GPU/NPU) - Só ocorre se houver movimento
                if motion_detected:
                    detections = self.detector.detect(frame, self.camera_id)
                    
                    for d in detections:
                        if d.get("plate_number"):
                            # Notifica o Django imediatamente via API interna
                            await self.api_client.send_sighting(
                                plate=d["plate_number"],
                                camera_id=self.camera_id,
                                vehicle_type=d.get("object_type", "unknown"),
                                confidence=d.get("plate_confidence", 0.0),
                                image_url=d.get("image_path")
                            )
                
                # Yield para o loop de eventos não travar
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Erro no loop de stream {self.camera_name}: {e}")
                await asyncio.sleep(5)