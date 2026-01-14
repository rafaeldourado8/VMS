from abc import ABC, abstractmethod
from typing import Optional
from admin.domain.entities import User


class IUserRepository(ABC):
    """Interface para repositório de usuários."""
    
    @abstractmethod
    def save(self, user: User) -> User:
        """Salva um usuário."""
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        """Busca usuário por ID."""
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email."""
        pass
    
    @abstractmethod
    def find_all(self) -> list[User]:
        """Lista todos os usuários."""
        pass
    
    @abstractmethod
    def delete(self, user_id: str) -> None:
        """Deleta um usuário."""
        pass
    
    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """Verifica se email já existe."""
        pass
