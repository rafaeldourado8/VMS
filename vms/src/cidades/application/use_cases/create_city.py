from dataclasses import dataclass
from uuid import uuid4
from domain.entities.city import City
from domain.repositories.city_repository import ICityRepository

@dataclass
class CreateCityRequest:
    name: str
    slug: str
    plan: str

class CreateCityUseCase:
    def __init__(self, repo: ICityRepository):
        self._repo = repo
    
    def execute(self, request: CreateCityRequest) -> str:
        existing = self._repo.find_by_slug(request.slug)
        if existing:
            raise ValueError(f"City with slug '{request.slug}' already exists")
        
        city = City(
            id=str(uuid4()),
            name=request.name,
            slug=request.slug,
            plan=request.plan
        )
        
        self._repo.save(city)
        return city.id
