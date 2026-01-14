from uuid import uuid4
import hashlib
from admin.domain import User, IUserRepository
from admin.application.dtos import CreateUserDTO


class CreateUserUseCase:
    """Use case para criar usuário."""
    
    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository
    
    def execute(self, dto: CreateUserDTO) -> User:
        """Cria um novo usuário."""
        # Valida email único
        if self._user_repo.exists_by_email(dto.email):
            raise ValueError(f"Email {dto.email} já está em uso")
        
        # Hash da senha
        password_hash = self._hash_password(dto.password)
        
        # Cria usuário
        user = User(
            id=str(uuid4()),
            email=dto.email,
            name=dto.name,
            password_hash=password_hash,
            city_ids=dto.city_ids,
            is_admin=dto.is_admin
        )
        
        return self._user_repo.save(user)
    
    def _hash_password(self, password: str) -> str:
        """Gera hash SHA256 da senha."""
        return hashlib.sha256(password.encode()).hexdigest()
