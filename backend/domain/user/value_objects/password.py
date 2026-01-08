from dataclasses import dataclass
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    VIEWER = "viewer"

@dataclass(frozen=True)
class Password:
    """Value object para senha (hash)"""
    
    hashed_value: str
    
    def __post_init__(self):
        if not self.hashed_value:
            raise ValueError("Hash da senha não pode ser vazio")
    
    def __str__(self) -> str:
        return "***"  # Nunca expor a senha