from typing import List, Optional
from datetime import datetime
from domain.detection.entities.detection import Detection
from domain.detection.repositories.detection_repository import DetectionRepository
from apps.deteccoes.models import Deteccao as DetectionModel
from .detection_mapper import DetectionMapper


class DjangoDetectionRepository(DetectionRepository):
    """Implementação Django do repositório de detecções"""
    
    def save(self, detection: Detection) -> Detection:
        """Salva uma detecção"""
        model = DetectionMapper.to_model(detection)
        model.save()
        return DetectionMapper.to_domain(model)
    
    def find_by_id(self, detection_id: int) -> Optional[Detection]:
        """Busca detecção por ID"""
        try:
            model = DetectionModel.objects.get(id=detection_id)
            return DetectionMapper.to_domain(model)
        except DetectionModel.DoesNotExist:
            return None
    
    def find_by_camera(self, camera_id: int, limit: int = 100) -> List[Detection]:
        """Busca detecções por câmera"""
        models = DetectionModel.objects.filter(camera_id=camera_id)[:limit]
        return [DetectionMapper.to_domain(m) for m in models]
    
    def find_by_plate(self, plate: str) -> List[Detection]:
        """Busca detecções por placa"""
        models = DetectionModel.objects.filter(plate__icontains=plate)
        return [DetectionMapper.to_domain(m) for m in models]
    
    def find_by_period(self, start: datetime, end: datetime) -> List[Detection]:
        """Busca detecções por período"""
        models = DetectionModel.objects.filter(
            timestamp__gte=start,
            timestamp__lte=end
        )
        return [DetectionMapper.to_domain(m) for m in models]
