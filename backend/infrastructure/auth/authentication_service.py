from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from domain.user import Email, UserRepository
from domain.user.exceptions import InvalidCredentialsException

class AuthenticationService:
    """Serviço de autenticação usando DDD"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def authenticate_user(self, email: str, password: str) -> dict:
        """Autentica usuário e retorna tokens"""
        
        # Usar autenticação Django para validar senha
        django_user = authenticate(username=email, password=password)
        if not django_user:
            raise InvalidCredentialsException("Email ou senha inválidos")
        
        # Buscar usuário no domínio
        domain_user = self.user_repository.find_by_email(Email(email))
        if not domain_user or not domain_user.is_active:
            raise InvalidCredentialsException("Usuário inativo ou não encontrado")
        
        # Gerar tokens
        refresh = RefreshToken.for_user(django_user)
        
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": domain_user.id,
                "email": domain_user.email.value,
                "name": domain_user.name.value,
                "role": domain_user.role.value,
                "is_staff": domain_user.is_staff
            }
        }