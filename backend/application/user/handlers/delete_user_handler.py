from ..commands.delete_user_command import DeleteUserCommand

from domain.user import UserRepository
from domain.user.exceptions import UserNotFoundException

class DeleteUserHandler:
    """Handler para deletar usuário"""
    
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def handle(self, command: DeleteUserCommand) -> None:
        """Executa o use case de deletar usuário"""
        
        user = self.repository.find_by_id(command.user_id)
        
        if not user:
            raise UserNotFoundException(f"Usuário {command.user_id} não encontrado")
        
        self.repository.delete(command.user_id)