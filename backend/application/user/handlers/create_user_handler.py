from ..commands.create_user_command import CreateUserCommand

from django.contrib.auth.hashers import make_password

from domain.user import User, Email, Username, Password, UserRole, UserRepository
from domain.user.exceptions import UserAlreadyExistsException

class CreateUserHandler:
    """Handler para criar usuário"""
    
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def handle(self, command: CreateUserCommand) -> User:
        """Executa o use case de criar usuário"""
        
        email = Email(command.email)
        
        if self.repository.exists_by_email(email):
            raise UserAlreadyExistsException(f"Usuário com email {command.email} já existe")
        
        name = Username(command.name)
        role = UserRole(command.role)
        password_hash = Password(make_password(command.password))
        
        user = User(
            id=None,
            email=email,
            name=name,
            role=role,
            is_staff=command.is_staff,
            password_hash=password_hash
        )
        
        return self.repository.save(user)