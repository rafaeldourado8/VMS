from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime
import numpy as np
from domain.entities.detection import Detection
from domain.repositories.detection_repository import IDetectionRepository
from domain.repositories.blacklist_repository import IBlacklistRepository
from domain.repositories.detection_provider import IDetectionProvider

@dataclass
class ProcessFrameRequest:
    camera_id: str
    city_id: str
    frame: np.ndarray

class ProcessFrameUseCase:
    def __init__(
        self,
        detection_repo: IDetectionRepository,
        blacklist_repo: IBlacklistRepository,
        provider: IDetectionProvider
    ):
        self._detection_repo = detection_repo
        self._blacklist_repo = blacklist_repo
        self._provider = provider
    
    def execute(self, request: ProcessFrameRequest) -> list[Detection]:
        # Detecta placas no frame
        results = self._provider.detect_plates(request.frame)
        
        detections = []
        for result in results:
            if result['confidence'] < 0.75:
                continue
            
            detection = Detection(
                id=str(uuid4()),
                camera_id=request.camera_id,
                plate=result['plate'],
                confidence=result['confidence'],
                image_url=f"/detections/{uuid4()}.jpg",  # Será salvo depois
                detected_at=datetime.now(),
                city_id=request.city_id
            )
            
            self._detection_repo.save(detection)
            detections.append(detection)
            
            # Verifica blacklist
            blacklist_entry = self._blacklist_repo.find_by_plate(
                detection.plate,
                request.city_id
            )
            if blacklist_entry and blacklist_entry.matches(detection.plate):
                # TODO: Enviar alerta
                pass
        
        return detections
