# VMS/fastapi_services/ai_detection/app/services/detection_service.py

import asyncio
import logging
import base64
import numpy as np
import cv2
from datetime import datetime
from typing import Dict, Optional, List, AsyncGenerator

from ..services.model_manager import ModelManager
from ..schemas import DetectionConfig, DetectionResult, Detection

logger = logging.getLogger(__name__)

class DetectionService:
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.detection_tasks: Dict[str, asyncio.Task] = {}
        logger.info("DetectionService initialized")

    async def process_stream(self, camera_id: str, config: DetectionConfig) -> AsyncGenerator[DetectionResult, None]:
        """Simulates processing a stream."""
        logger.info(f"Iniciando stream simulado para: {camera_id}")
        try:
            while True:
                # Simula obter um frame e processar
                await asyncio.sleep(1.0 / config.fps) # Simula FPS
                
                # Simula uma deteção
                detections = [
                    Detection(
                        bbox=[10, 10, 100, 100], # [x1, y1, x2, y2]
                        confidence=0.99,
                        class_name="simulated_car",
                        class_id=2 
                    )
                ]
                
                result = DetectionResult(
                    camera_id=camera_id,
                    timestamp=datetime.now(),
                    detections=detections,
                    total_detections=len(detections),
                    processing_time=10.0
                )
                yield result
        except asyncio.CancelledError:
            logger.info(f"Stream para {camera_id} cancelado.")
        except Exception as e:
            logger.error(f"Erro no stream simulado {camera_id}: {e}")
        finally:
            logger.info(f"Parando stream simulado para {camera_id}")

    async def detect_single_frame(self, camera_id: str, frame_base64: str, confidence: float, classes: Optional[list]) -> DetectionResult:
        """Simula deteção num único frame."""
        logger.info(f"Processando frame único para {camera_id}")
        
        # Simula uma deteção
        detections = [
            Detection(
                bbox=[20, 20, 150, 150],
                confidence=confidence,
                class_name=classes[0] if classes else "simulated_object",
                class_id=0
            )
        ]
        
        return DetectionResult(
            camera_id=camera_id,
            timestamp=datetime.now(),
            detections=detections,
            total_detections=len(detections),
            processing_time=50.0
        )

    async def stop_detection(self, camera_id: str) -> bool:
        """Para uma tarefa de deteção em execução."""
        task = self.detection_tasks.pop(camera_id, None)
        if task:
            task.cancel()
            logger.info(f"Parada deteção para {camera_id}")
            return True
        logger.warning(f"Nenhuma tarefa de deteção encontrada para parar em {camera_id}")
        return False

    async def cleanup(self):
        """Limpa todas as tarefas em execução."""
        logger.info("Limpando todas as tarefas de deteção...")
        tasks_to_cancel = list(self.detection_tasks.values())
        for task in tasks_to_cancel:
            task.cancel()
        await asyncio.gather(*tasks_to_cancel, return_exceptions=True)
        self.detection_tasks.clear()
        logger.info("Limpeza completa.")