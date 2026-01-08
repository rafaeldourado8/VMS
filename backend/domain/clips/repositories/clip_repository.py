from ..entities.clip import Clip
from abc import ABC, abstractmethod
from typing import List, Optional

class ClipRepository(ABC):
    """Interface do repositório de clips"""
    
    @abstractmethod
    def create_clip(self, clip: Clip) -> Clip:
        """Cria um novo clip"""
        pass
    
    @abstractmethod
    def get_clips_by_user(self, user_id: int) -> List[Clip]:
        """Busca clips de um usuário"""
        pass
    
    @abstractmethod
    def get_clip_by_id(self, clip_id: int) -> Optional[Clip]:
        """Busca clip por ID"""
        pass
    
    @abstractmethod
    def delete_clip(self, clip_id: int) -> bool:
        """Remove um clip"""
        pass