import hashlib
from typing import Protocol
from admin.domain import User, IUserRepository
from admin.application.dtos import AuthenticateDTO


class IJWTService(Protocol):
    """Interface para serviço JWT."""
    
    def generate_token(self, payload: dict) -> str:
        """Gera token JWT."""
        ...


class AuthenticateUserUseCase:
    """Use case para autenticar usuário."""
    
    def __init__(self, user_repository: IUserRepository, jwt_service: IJWTService):
        self._user_repo = user_repository
        self._jwt_service = jwt_service
    
    def execute(self, dto: AuthenticateDTO) -> dict:
        """Autentica usuário e retorna token."""
        user = self._user_repo.find_by_email(dto.email)
        
        if not user:
            raise ValueError("Credenciais inválidas")
        
        if not user.is_active:
            raise ValueError("Usuário inativo")
        
        # Verifica senha
        password_hash = self._hash_password(dto.password)
        if password_hash != user.password_hash:
            raise ValueError("Credenciais inválidas")
        
        # Gera token
        token = self._jwt_service.generate_token({
            "user_id": user.id,
            "email": user.email,
            "is_admin": user.is_admin,
            "city_ids": user.city_ids
        })
        
        return {
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_admin": user.is_admin,
                "city_ids": user.city_ids
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Gera hash SHA256 da senha."""
        return hashlib.sha256(password.encode()).hexdigest()
