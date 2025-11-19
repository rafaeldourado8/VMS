import logging
from django.db import transaction
from .models import Deteccao
from apps.cameras.models import Camera
from .serializers import IngestDeteccaoSerializer

logger = logging.getLogger(__name__)

class DetectionProcessor:
    """
    Responsável exclusivamente por validar dados brutos e persistir uma detecção.
    Segue o SRP (Single Responsibility Principle).
    """
    
    def process_raw_data(self, data: dict) -> Deteccao:
        """
        Recebe um dicionário (JSON parsed), valida e salva no banco.
        Retorna a instância criada ou levanta exceção.
        """
        serializer = IngestDeteccaoSerializer(data=data)
        
        if not serializer.is_valid():
            error_msg = f"Dados de detecção inválidos: {serializer.errors}"
            logger.warning(error_msg)
            raise ValueError(error_msg)

        validated_data = serializer.validated_data
        camera_id = validated_data.get('camera_id')
        
        try:
            camera = Camera.objects.get(id=camera_id)
        except Camera.DoesNotExist:
            error_msg = f"Câmara com ID {camera_id} não encontrada. Detecção descartada."
            logger.error(error_msg)
            raise ValueError(error_msg)

        validated_data['camera'] = camera
        
        if 'camera_id' in validated_data:
            validated_data.pop('camera_id')
            
        with transaction.atomic():
            deteccao = Deteccao.objects.create(**validated_data)
            
        logger.info(f"Detecção salva: {deteccao} para câmara {camera.name}")
        return deteccao