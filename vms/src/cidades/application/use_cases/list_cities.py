from domain.entities.city import City
from domain.repositories.city_repository import ICityRepository

class ListCitiesUseCase:
    def __init__(self, repo: ICityRepository):
        self._repo = repo
    
    def execute(self) -> list[City]:
        return self._repo.list_all()
