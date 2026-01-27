from typing import Optional, List
from uuid import UUID
from shared.admin.cameras.models import Camera
from .camera_repository import CameraRepository

class DjangoCameraRepository(CameraRepository):
    
    def get_by_id(self, camera_id: UUID, city_id: UUID):
        try:
            return Camera.objects.get(id=camera_id, city_id=city_id)
        except Camera.DoesNotExist:
            return None
    
    def get_by_public_id(self, public_id: UUID, city_id: UUID):
        try:
            return Camera.objects.get(public_id=public_id, city_id=city_id)
        except Camera.DoesNotExist:
            return None
    
    def list_by_city(self, city_id: UUID, is_active: Optional[bool] = None) -> List:
        queryset = Camera.objects.filter(city_id=city_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return list(queryset)
    
    def exists(self, camera_id: UUID, city_id: UUID) -> bool:
        return Camera.objects.filter(id=camera_id, city_id=city_id).exists()
    
    def count_by_city(self, city_id: UUID) -> int:
        return Camera.objects.filter(city_id=city_id).count()
    
    def update_recording_status(self, camera_id: UUID, city_id: UUID, enabled: bool) -> bool:
        try:
            updated = Camera.objects.filter(id=camera_id, city_id=city_id).update(recording_enabled=enabled)
            return updated > 0
        except Exception:
            return False
