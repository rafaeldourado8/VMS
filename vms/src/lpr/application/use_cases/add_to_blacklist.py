from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime
from domain.entities.blacklist_entry import BlacklistEntry
from domain.repositories.blacklist_repository import IBlacklistRepository

@dataclass
class AddToBlacklistRequest:
    plate: str
    reason: str
    city_id: str

class AddToBlacklistUseCase:
    def __init__(self, repo: IBlacklistRepository):
        self._repo = repo
    
    def execute(self, request: AddToBlacklistRequest) -> str:
        # Verifica se já existe
        existing = self._repo.find_by_plate(request.plate, request.city_id)
        if existing and existing.is_active:
            raise ValueError(f"Plate {request.plate} already in blacklist")
        
        entry = BlacklistEntry(
            id=str(uuid4()),
            plate=request.plate.upper(),
            reason=request.reason,
            city_id=request.city_id,
            created_at=datetime.now()
        )
        
        self._repo.save(entry)
        return entry.id
