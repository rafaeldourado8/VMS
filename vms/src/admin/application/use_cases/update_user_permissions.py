from admin.domain import User, IUserRepository


class UpdateUserPermissionsUseCase:
    """Use case para atualizar permissões de usuário."""
    
    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository
    
    def execute(self, user_id: str, city_ids: list[str], is_admin: bool = False) -> User:
        """Atualiza permissões de acesso do usuário."""
        user = self._user_repo.find_by_id(user_id)
        
        if not user:
            raise ValueError(f"Usuário {user_id} não encontrado")
        
        # Atualiza permissões
        user.city_ids = city_ids
        user.is_admin = is_admin
        
        return self._user_repo.save(user)
