from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Location:
    """Value Object para localização da câmera"""
    
    name: Optional[str]
    
    def __str__(self) -> str:
        return self.name or "Sem localização"
