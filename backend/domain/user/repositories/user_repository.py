from ..entities.user import User
from ..value_objects.email import Email
from abc import ABC, abstractmethod
from typing import List, Optional

class UserRepository(ABC):
    """Interface de repositório para User"""
    
    @abstractmethod
    def save(self, user: User) -> User:
        """Salva ou atualiza um usuário"""
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Busca usuário por ID"""
        pass
    
    @abstractmethod
    def find_by_email(self, email: Email) -> Optional[User]:
        """Busca usuário por email"""
        pass
    
    @abstractmethod
    def find_all_active(self) -> List[User]:
        """Busca todos os usuários ativos"""
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> None:
        """Remove um usuário"""
        pass
    
    @abstractmethod
    def exists_by_email(self, email: Email) -> bool:
        """Verifica se existe usuário com o email"""
        pass