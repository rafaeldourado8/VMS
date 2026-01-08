from ..value_objects.email import Email
from ..value_objects.password import Password, UserRole
from ..value_objects.username import Username
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """Entidade de domínio User"""
    
    id: Optional[int]
    email: Email
    name: Username
    role: UserRole = UserRole.VIEWER
    is_active: bool = True
    is_staff: bool = False
    created_at: Optional[datetime] = None
    password_hash: Optional[Password] = None
    
    def activate(self) -> None:
        """Ativa o usuário"""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Desativa o usuário"""
        self.is_active = False
    
    def make_admin(self) -> None:
        """Torna o usuário administrador"""
        self.role = UserRole.ADMIN
        self.is_staff = True
    
    def make_viewer(self) -> None:
        """Torna o usuário visualizador"""
        self.role = UserRole.VIEWER
        self.is_staff = False
    
    def is_admin(self) -> bool:
        """Verifica se o usuário é administrador"""
        return self.role == UserRole.ADMIN
    
    def can_manage_users(self) -> bool:
        """Verifica se pode gerenciar usuários"""
        return self.is_admin() and self.is_active
    
    def can_access_cameras(self) -> bool:
        """Verifica se pode acessar câmeras"""
        return self.is_active