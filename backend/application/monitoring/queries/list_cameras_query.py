from dataclasses import dataclass


@dataclass
class ListCamerasQuery:
    """Query para listar câmeras de um usuário"""
    
    owner_id: int
