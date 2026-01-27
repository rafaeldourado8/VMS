from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from .models import StreamingSession

class StreamingManager(ABC):
    
    @abstractmethod
    def start_stream(self, camera_id: UUID, city_id: UUID, user_id: int) -> StreamingSession:
        """
        Inicia stream de uma câmera.
        Assume que tenant_id já foi validado pelo middleware.
        Retorna StreamingSession com session_id.
        """
        pass
    
    @abstractmethod
    def stop_stream(self, session_id: str, city_id: UUID) -> bool:
        """
        Para stream e destrói recursos.
        Retorna True se parou com sucesso.
        """
        pass
    
    @abstractmethod
    def get_session(self, session_id: str, city_id: UUID) -> Optional[StreamingSession]:
        """
        Busca sessão ativa.
        Sempre valida city_id.
        """
        pass
    
    @abstractmethod
    def list_active_sessions(self, city_id: UUID) -> list[StreamingSession]:
        """
        Lista todas as sessões ativas de uma cidade.
        """
        pass
    
    @abstractmethod
    def count_active_sessions(self, city_id: UUID) -> int:
        """
        Conta sessões ativas de uma cidade.
        """
        pass
