from ..queries.get_user_query import GetUserQuery

from domain.user import User, UserRepository
from domain.user.exceptions import UserNotFoundException

class GetUserHandler:
    """Handler para buscar usuário"""
    
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def handle(self, query: GetUserQuery) -> User:
        """Executa o use case de buscar usuário"""
        
        user = self.repository.find_by_id(query.user_id)
        
        if not user:
            raise UserNotFoundException(f"Usuário {query.user_id} não encontrado")
        
        return user