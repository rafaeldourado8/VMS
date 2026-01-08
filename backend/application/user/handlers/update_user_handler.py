from ..commands.update_user_command import UpdateUserCommand

from domain.user import User, Username, UserRole, UserRepository
from domain.user.exceptions import UserNotFoundException

class UpdateUserHandler:
    """Handler para atualizar usuário"""
    
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def handle(self, command: UpdateUserCommand) -> User:
        """Executa o use case de atualizar usuário"""
        
        user = self.repository.find_by_id(command.user_id)
        
        if not user:
            raise UserNotFoundException(f"Usuário {command.user_id} não encontrado")
        
        if command.name:
            user.name = Username(command.name)
        
        if command.role:
            user.role = UserRole(command.role)
            if command.role == "admin":
                user.make_admin()
            else:
                user.make_viewer()
        
        if command.is_active is not None:
            if command.is_active:
                user.activate()
            else:
                user.deactivate()
        
        return self.repository.save(user)