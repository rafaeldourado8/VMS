from typing import Optional

from apps.usuarios.models import Usuario
from domain.user import User, Email, Username, Password, UserRole

class UserMapper:
    """Mapper entre entidade User e modelo Django Usuario"""
    
    @staticmethod
    def to_domain(model: Usuario) -> User:
        """Converte modelo Django para entidade User"""
        return User(
            id=model.id,
            email=Email(model.email),
            name=Username(model.name),
            role=UserRole(model.role),
            is_active=model.is_active,
            is_staff=model.is_staff,
            created_at=model.created_at,
            password_hash=Password(model.password) if model.password else None
        )
    
    @staticmethod
    def to_model(user: User, model: Optional[Usuario] = None) -> Usuario:
        """Converte entidade User para modelo Django"""
        if model is None:
            model = Usuario()
        
        model.email = user.email.value
        model.name = user.name.value
        model.role = user.role.value
        model.is_active = user.is_active
        model.is_staff = user.is_staff
        
        if user.password_hash:
            model.password = user.password_hash.hashed_value
        
        return model