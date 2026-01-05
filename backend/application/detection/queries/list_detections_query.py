from dataclasses import dataclass
from typing import Optional


@dataclass
class ListDetectionsQuery:
    """Query para listar detecções"""
    
    owner_id: int
    camera_id: Optional[int] = None
    plate: Optional[str] = None
    limit: int = 100
