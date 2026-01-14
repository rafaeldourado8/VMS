from domain.repositories.city_repository import ICityRepository
from domain.entities.city import City
from .models import CityModel

class DjangoCityRepository(ICityRepository):
    def save(self, city: City) -> None:
        model = CityModel.from_entity(city)
        model.save()
    
    def find_by_id(self, city_id: str) -> City | None:
        try:
            model = CityModel.objects.get(id=city_id)
            return model.to_entity()
        except CityModel.DoesNotExist:
            return None
    
    def find_by_slug(self, slug: str) -> City | None:
        try:
            model = CityModel.objects.get(slug=slug)
            return model.to_entity()
        except CityModel.DoesNotExist:
            return None
    
    def list_all(self) -> list[City]:
        return [model.to_entity() for model in CityModel.objects.all()]
    
    def delete(self, city_id: str) -> None:
        CityModel.objects.filter(id=city_id).delete()
