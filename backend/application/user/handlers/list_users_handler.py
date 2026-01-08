from ..queries.list_users_query import ListUsersQuery
from typing import List

from domain.user import User, UserRepository

class ListUsersHandler:
    """Handler para listar usuários"""
    
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def handle(self, query: ListUsersQuery) -> List[User]:
        """Executa o use case de listar usuários"""
        
        if query.active_only:
            return self.repository.find_all_active()
        
        # Para simplificar, retornamos apenas ativos por enquanto
        return self.repository.find_all_active()