from .models import Deteccao
from .schemas import IngestDeteccaoDTO
from typing import Optional
import logging

from django.db import transaction

from apps.cameras.models import Camera

logger = logging.getLogger(__name__)

class DeteccaoService:
    """Serviço para gestão de detecções e ingestão de dados da IA."""

    @staticmethod
    def process_ingestion(data: IngestDeteccaoDTO) -> Deteccao:
        """Processa e persiste uma nova detecção vinda da ingestão."""
        try:
            camera = Camera.objects.get(id=data.camera_id)
        except Camera.DoesNotExist:
            logger.error(f"Câmara ID {data.camera_id} não encontrada. Ingestão abortada.")
            raise ValueError(f"Câmara {data.camera_id} inexistente.")

        with transaction.atomic():
            deteccao = Deteccao.objects.create(
                camera=camera,
                plate=data.plate,
                confidence=data.confidence,
                timestamp=data.timestamp,
                vehicle_type=data.vehicle_type,
                image_url=data.image_url,
                video_url=data.video_url
            )
        
        logger.info(f"Detecção {deteccao.id} salva para câmara {camera.name}")
        return deteccao

    @staticmethod
    def list_for_user(user, camera_id: Optional[int] = None, plate: Optional[str] = None):
        """
        Lista detecções baseadas nas permissões do utilizador e filtros opcionais.
        O uso de filtros do ORM garante que os parâmetros sejam escapados, 
        prevenindo SQL Injection.
        """
        queryset = Deteccao.objects.filter(camera__owner=user).select_related("camera")
        
        if camera_id:
            queryset = queryset.filter(camera_id=camera_id)
            
        if plate:
            # Filtro por placa (case-insensitive)
            queryset = queryset.filter(plate__icontains=plate)
            
        return queryset