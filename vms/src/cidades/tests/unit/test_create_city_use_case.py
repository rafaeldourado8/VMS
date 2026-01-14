import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from application.use_cases.create_city import CreateCityUseCase, CreateCityRequest
from domain.entities.city import City

class InMemoryCityRepository:
    def __init__(self):
        self.cities = {}
    
    def save(self, city: City) -> None:
        self.cities[city.id] = city
    
    def find_by_id(self, city_id: str) -> City | None:
        return self.cities.get(city_id)
    
    def find_by_slug(self, slug: str) -> City | None:
        for city in self.cities.values():
            if city.slug == slug:
                return city
        return None
    
    def list_all(self) -> list[City]:
        return list(self.cities.values())
    
    def delete(self, city_id: str) -> None:
        self.cities.pop(city_id, None)

def test_create_city_success():
    repo = InMemoryCityRepository()
    use_case = CreateCityUseCase(repo)
    
    request = CreateCityRequest(
        name='São Paulo',
        slug='sao_paulo',
        plan='basic'
    )
    
    city_id = use_case.execute(request)
    
    assert city_id is not None
    city = repo.find_by_id(city_id)
    assert city.name == 'São Paulo'
    assert city.slug == 'sao_paulo'
    assert city.plan == 'basic'

def test_create_city_duplicate_slug():
    repo = InMemoryCityRepository()
    use_case = CreateCityUseCase(repo)
    
    request = CreateCityRequest(name='City 1', slug='test', plan='basic')
    use_case.execute(request)
    
    with pytest.raises(ValueError, match="already exists"):
        request2 = CreateCityRequest(name='City 2', slug='test', plan='pro')
        use_case.execute(request2)
