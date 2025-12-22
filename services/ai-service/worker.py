import asyncio
import cv2
import numpy as np
import logging
import time
from detector import VehicleDetector
from queue_manager import QueueManager
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

processed_counter = Counter('detections_processed_total', 'Total detections processed')
processing_time = Histogram('detection_processing_seconds', 'Time spent processing')
queue_size_gauge = Gauge('detection_queue_size', 'Current queue size')

class DetectionWorker:
    def __init__(self):
        self.detector = VehicleDetector()
        self.queue = QueueManager()
        self.running = False
        self.stats = {
            "processed": 0,
            "total_time": 0.0
        }
    
    async def start(self):
        await self.queue.connect()
        self.running = True
        logger.info("Worker started")
        
        while self.running:
            try:
                task = await self.queue.dequeue()
                if task:
                    await self._process_task(task)
                
                queue_size = await self.queue.get_queue_size()
                queue_size_gauge.set(queue_size)
                
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(1)
    
    async def stop(self):
        self.running = False
        await self.queue.disconnect()
        logger.info("Worker stopped")
    
    async def _process_task(self, task: dict):
        start = time.time()
        
        try:
            image_bytes = bytes.fromhex(task["image_data"])
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            detections = self.detector.detect(image)
            
            processing_time_ms = (time.time() - start) * 1000
            
            result = {
                "camera_id": task["camera_id"],
                "detections": detections,
                "processing_time_ms": processing_time_ms
            }
            
            await self.queue.store_result(task["task_id"], result)
            
            self.stats["processed"] += 1
            self.stats["total_time"] += processing_time_ms
            
            processed_counter.inc()
            processing_time.observe(time.time() - start)
            
            logger.debug(f"Processed {task['task_id']} in {processing_time_ms:.2f}ms")
            
        except Exception as e:
            logger.error(f"Task processing error: {e}")
