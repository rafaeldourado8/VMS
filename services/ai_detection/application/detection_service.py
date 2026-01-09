from typing import List, Dict, Any
from domain.detection_result import DetectionResult
from infrastructure.detection_repository import DetectionRepository
from infrastructure.detection_publisher import DetectionPublisher
from infrastructure.providers.rekognition import RekognitionProvider
import logging

logger = logging.getLogger(__name__)


class DetectionService:
    def __init__(self, repository: DetectionRepository, publisher: DetectionPublisher):
        self.repository = repository
        self.publisher = publisher
        self.provider = RekognitionProvider()
    
    async def process_frame(self, camera_id: str, frame_bytes: bytes) -> DetectionResult:
        # Detect with Rekognition
        labels = await self.provider.detect_labels(frame_bytes)
        faces = await self.provider.detect_faces(frame_bytes)
        
        # Combine results
        all_detections = labels + faces
        
        # Calculate average confidence
        confidence_avg = 0.0
        if all_detections:
            confidence_avg = sum(d.get('confidence', 0) for d in all_detections) / len(all_detections)
        
        # Normalize to DetectionResult
        result = DetectionResult(
            camera_id=camera_id,
            provider='rekognition',
            detections=all_detections,
            confidence_avg=confidence_avg
        )
        
        # Persist to PostgreSQL
        result_id = await self.repository.save(result)
        logger.info(f"Saved detection {result_id} for camera {camera_id}")
        
        # Publish to RabbitMQ
        await self.publisher.publish(result)
        logger.info(f"Published detection for camera {camera_id}")
        
        return result
