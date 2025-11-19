import logging
from typing import Protocol, List, Dict, Any
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Camera

logger = logging.getLogger(__name__)
User = get_user_model()

class ICameraService(Protocol):
    """
    Interface (Protocol) para garantir o Princípio da Inversão de Dependência (DIP).
    Define o contrato que qualquer serviço de câmara deve seguir.
    """
    def create_camera(self, user: User, data: Dict[str, Any]) -> Camera:
        ...

    def list_cameras_for_user(self, user: User) -> List[Camera]:
        ...

class CameraService:
    """
    Implementação concreta da lógica de negócio (SRP).
    """
    
    def create_camera(self, user: User, data: Dict[str, Any]) -> Camera:
        """
        Cria uma câmara associada ao utilizador.
        Aqui centralizamos regras de negócio (ex: validação de limites de câmaras).
        """
        # CORREÇÃO APLICADA AQUI: user.username -> user.email
        logger.info(f"A criar nova câmara para o utilizador: {user.email}")
        
        # Exemplo de regra de negócio futura:
        # if user.cameras.count() >= user.plan.max_cameras:
        #     raise ValidationError("Limite de câmaras atingido.")

        with transaction.atomic():
            # Remove owner do dicionário se existir, pois vamos atribuir explicitamente
            if 'owner' in data:
                data.pop('owner')
            
            camera = Camera(**data)
            camera.owner = user
            camera.save()
            
        logger.info(f"Câmara '{camera.name}' criada com sucesso (ID: {camera.id})")
        return camera

    def list_cameras_for_user(self, user: User):
        """
        Retorna as câmaras que o utilizador tem permissão de ver.
        """
        return Camera.objects.filter(owner=user).order_by("name")