from dataclasses import dataclass

@dataclass
class GetUserQuery:
    """Query para buscar usuário por ID"""
    
    user_id: int