from typing import List, Optional
from domain.monitoring.entities.camera import Camera
from domain.monitoring.repositories.camera_repository import CameraRepository
from apps.cameras.models import Camera as CameraModel
from .camera_mapper import CameraMapper


class DjangoCameraRepository(CameraRepository):
    """Implementação Django do repositório de câmeras"""
    
    def save(self, camera: Camera) -> Camera:
        """Salva ou atualiza uma câmera"""
        if camera.id:
            model = CameraModel.objects.get(id=camera.id)
            model = CameraMapper.to_model(camera, model)
        else:
            model = CameraMapper.to_model(camera)
        
        model.save()
        return CameraMapper.to_domain(model)
    
    def find_by_id(self, camera_id: int) -> Optional[Camera]:
        """Busca câmera por ID"""
        try:
            model = CameraModel.objects.get(id=camera_id)
            return CameraMapper.to_domain(model)
        except CameraModel.DoesNotExist:
            return None
    
    def find_by_owner(self, owner_id: int) -> List[Camera]:
        """Busca câmeras por proprietário"""
        models = CameraModel.objects.filter(owner_id=owner_id).order_by('-created_at')
        return [CameraMapper.to_domain(m) for m in models]
    
    def delete(self, camera_id: int) -> None:
        """Remove uma câmera"""
        CameraModel.objects.filter(id=camera_id).delete()
    
    def exists_by_name(self, name: str) -> bool:
        """Verifica se existe câmera com o nome"""
        return CameraModel.objects.filter(name=name).exists()
