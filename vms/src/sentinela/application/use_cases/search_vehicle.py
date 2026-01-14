from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime
from domain.entities.vehicle_search import VehicleSearch
from domain.repositories.vehicle_search_repository import IVehicleSearchRepository

@dataclass
class SearchVehicleRequest:
    city_id: str
    user_id: str
    plate: str | None = None
    color: str | None = None
    vehicle_type: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None

class SearchVehicleUseCase:
    def __init__(self, search_repo: IVehicleSearchRepository):
        self._search_repo = search_repo
    
    def execute(self, request: SearchVehicleRequest) -> str:
        # Valida critérios
        if not any([request.plate, request.color, request.vehicle_type]):
            raise ValueError("At least one search criteria is required")
        
        # Cria busca
        search = VehicleSearch(
            id=str(uuid4()),
            city_id=request.city_id,
            user_id=request.user_id,
            plate=request.plate,
            color=request.color,
            vehicle_type=request.vehicle_type,
            start_date=request.start_date or datetime.now(),
            end_date=request.end_date or datetime.now(),
            created_at=datetime.now()
        )
        
        self._search_repo.save(search)
        
        # Processamento será feito de forma assíncrona (Celery)
        # process_search_task.delay(search.id)
        
        return search.id
