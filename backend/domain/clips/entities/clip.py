from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class Clip:
    """Entidade de domínio para clips de vídeo"""
    
    id: Optional[int]
    owner_id: int
    camera_id: int
    name: str
    start_time: datetime
    end_time: datetime
    file_path: str
    thumbnail_path: Optional[str]
    duration_seconds: int
    created_at: datetime
    
    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Nome do clip não pode estar vazio")
        
        if self.start_time >= self.end_time:
            raise ValueError("Hora de início deve ser anterior à hora de fim")
        
        if self.duration_seconds <= 0:
            raise ValueError("Duração deve ser positiva")
    
    def get_duration_minutes(self) -> float:
        """Retorna duração em minutos"""
        return self.duration_seconds / 60.0