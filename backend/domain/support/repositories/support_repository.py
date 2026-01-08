from ..entities.support_message import SupportMessage
from abc import ABC, abstractmethod
from typing import List, Optional

class SupportRepository(ABC):
    """Interface do repositório de suporte"""
    
    @abstractmethod
    def create_message(self, message: SupportMessage) -> SupportMessage:
        """Cria uma nova mensagem de suporte"""
        pass
    
    @abstractmethod
    def get_messages_by_user(self, user_id: int) -> List[SupportMessage]:
        """Busca mensagens de um usuário"""
        pass
    
    @abstractmethod
    def get_all_messages(self) -> List[SupportMessage]:
        """Busca todas as mensagens (admin)"""
        pass
    
    @abstractmethod
    def get_message_by_id(self, message_id: int) -> Optional[SupportMessage]:
        """Busca mensagem por ID"""
        pass