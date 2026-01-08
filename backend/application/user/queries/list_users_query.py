from dataclasses import dataclass
from typing import Optional

@dataclass
class ListUsersQuery:
    """Query para listar usuários"""
    
    active_only: bool = True
    limit: int = 100