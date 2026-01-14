import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from application.use_cases.list_cities import ListCitiesUseCase
from domain.entities.city import City

class InMemoryCityRepository:
    def __init__(self, cities=None):
        self.cities = {c.id: c for c in (cities or [])}
    
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

def test_list_cities_empty():
    repo = InMemoryCityRepository()
    use_case = ListCitiesUseCase(repo)
    
    cities = use_case.execute()
    
    assert cities == []

def test_list_cities_with_data():
    cities = [
        City(id='1', name='São Paulo', slug='sp', plan='basic'),
        City(id='2', name='Rio de Janeiro', slug='rj', plan='pro'),
        City(id='3', name='Belo Horizonte', slug='bh', plan='premium')
    ]
    
    repo = InMemoryCityRepository(cities)
    use_case = ListCitiesUseCase(repo)
    
    result = use_case.execute()
    
    assert len(result) == 3
    assert result[0].name == 'São Paulo'
    assert result[1].name == 'Rio de Janeiro'
    assert result[2].name == 'Belo Horizonte'
