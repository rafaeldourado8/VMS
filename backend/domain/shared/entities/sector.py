from dataclasses import dataclass
from datetime import datetime


@dataclass
class Sector:
    """Entidade de Setor para controle de acesso"""
    id: int
    name: str
    description: str = ""
    created_at: datetime = None
