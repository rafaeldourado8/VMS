from .user_mapper import UserMapper
from typing import List, Optional

from apps.usuarios.models import Usuario
from domain.user import User, Email, UserRepository

class DjangoUserRepository(UserRepository):
    """Implementação Django do repositório de usuários"""
    
    def save(self, user: User) -> User:
        """Salva ou atualiza um usuário"""
        if user.id:
            model = Usuario.objects.get(id=user.id)
            model = UserMapper.to_model(user, model)
        else:
            model = UserMapper.to_model(user)
        
        model.save()
        return UserMapper.to_domain(model)
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Busca usuário por ID"""
        try:
            model = Usuario.objects.get(id=user_id)
            return UserMapper.to_domain(model)
        except Usuario.DoesNotExist:
            return None
    
    def find_by_email(self, email: Email) -> Optional[User]:
        """Busca usuário por email"""
        try:
            model = Usuario.objects.get(email=email.value)
            return UserMapper.to_domain(model)
        except Usuario.DoesNotExist:
            return None
    
    def find_all_active(self) -> List[User]:
        """Busca todos os usuários ativos"""
        models = Usuario.objects.filter(is_active=True).order_by('name')
        return [UserMapper.to_domain(m) for m in models]
    
    def delete(self, user_id: int) -> None:
        """Remove um usuário"""
        Usuario.objects.filter(id=user_id).delete()
    
    def exists_by_email(self, email: Email) -> bool:
        """Verifica se existe usuário com o email"""
        return Usuario.objects.filter(email=email.value).exists()