from domain.repositories.camera_repository import ICameraRepository
from domain.entities.camera import Camera
from .models import CameraModel

class DjangoCameraRepository(ICameraRepository):
    def save(self, camera: Camera) -> None:
        model = CameraModel.from_entity(camera)
        model.save()
    
    def find_by_id(self, camera_id: str) -> Camera | None:
        try:
            model = CameraModel.objects.get(id=camera_id)
            return model.to_entity()
        except CameraModel.DoesNotExist:
            return None
    
    def list_by_city(self, city_id: str) -> list[Camera]:
        return [m.to_entity() for m in CameraModel.objects.filter(city_id=city_id)]
    
    def count_by_city(self, city_id: str) -> int:
        return CameraModel.objects.filter(city_id=city_id).count()
    
    def count_lpr_by_city(self, city_id: str) -> int:
        return CameraModel.objects.filter(city_id=city_id, type='rtsp').count()
    
    def delete(self, camera_id: str) -> None:
        CameraModel.objects.filter(id=camera_id).delete()
