from domain.user import User
from domain.user.exceptions import InsufficientPermissionsException

class UserPermissions:
    """Lógica de permissões para usuários"""
    
    @staticmethod
    def can_create_user(current_user: User) -> bool:
        """Verifica se pode criar usuário"""
        return current_user.can_manage_users()
    
    @staticmethod
    def can_update_user(current_user: User, target_user: User) -> bool:
        """Verifica se pode atualizar usuário"""
        # Admin pode atualizar qualquer usuário
        if current_user.can_manage_users():
            return True
        
        # Usuário pode atualizar a si mesmo (dados básicos)
        return current_user.id == target_user.id
    
    @staticmethod
    def can_delete_user(current_user: User, target_user: User) -> bool:
        """Verifica se pode deletar usuário"""
        # Apenas admin pode deletar
        if not current_user.can_manage_users():
            return False
        
        # Não pode deletar a si mesmo
        return current_user.id != target_user.id
    
    @staticmethod
    def can_list_users(current_user: User) -> bool:
        """Verifica se pode listar usuários"""
        return current_user.can_manage_users()
    
    @staticmethod
    def ensure_can_create_user(current_user: User) -> None:
        """Garante que pode criar usuário"""
        if not UserPermissions.can_create_user(current_user):
            raise InsufficientPermissionsException("Sem permissão para criar usuários")
    
    @staticmethod
    def ensure_can_update_user(current_user: User, target_user: User) -> None:
        """Garante que pode atualizar usuário"""
        if not UserPermissions.can_update_user(current_user, target_user):
            raise InsufficientPermissionsException("Sem permissão para atualizar este usuário")
    
    @staticmethod
    def ensure_can_delete_user(current_user: User, target_user: User) -> None:
        """Garante que pode deletar usuário"""
        if not UserPermissions.can_delete_user(current_user, target_user):
            raise InsufficientPermissionsException("Sem permissão para deletar este usuário")