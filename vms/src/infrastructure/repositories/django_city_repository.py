from typing import Optional, List
from uuid import UUID
from shared.admin.cidades.models import City
from shared.admin.cidades.enums import CityStatus
from .city_repository import CityRepository

class DjangoCityRepository(CityRepository):
    
    def get_by_id(self, city_id: UUID):
        try:
            return City.objects.get(id=city_id)
        except City.DoesNotExist:
            return None
    
    def get_by_name(self, name: str):
        try:
            return City.objects.get(name=name)
        except City.DoesNotExist:
            return None
    
    def list_active(self) -> List:
        return list(City.objects.filter(status=CityStatus.ACTIVE))
    
    def exists(self, city_id: UUID) -> bool:
        return City.objects.filter(id=city_id).exists()
