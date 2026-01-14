from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Entidade de usuário do sistema."""
    
    id: str
    email: str
    name: str
    password_hash: str
    city_ids: list[str] = field(default_factory=list)
    is_admin: bool = False
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.email or "@" not in self.email:
            raise ValueError("Email inválido")
        if not self.name or len(self.name) < 3:
            raise ValueError("Nome deve ter no mínimo 3 caracteres")
        if not self.password_hash:
            raise ValueError("Password hash é obrigatório")
    
    def can_access_city(self, city_id: str) -> bool:
        """Verifica se usuário pode acessar uma cidade."""
        return self.is_admin or city_id in self.city_ids
    
    def add_city_access(self, city_id: str) -> None:
        """Adiciona acesso a uma cidade."""
        if city_id not in self.city_ids:
            self.city_ids.append(city_id)
            self.updated_at = datetime.now()
    
    def remove_city_access(self, city_id: str) -> None:
        """Remove acesso a uma cidade."""
        if city_id in self.city_ids:
            self.city_ids.remove(city_id)
            self.updated_at = datetime.now()
    
    def deactivate(self) -> None:
        """Desativa o usuário."""
        self.is_active = False
        self.updated_at = datetime.now()
    
    def activate(self) -> None:
        """Ativa o usuário."""
        self.is_active = True
        self.updated_at = datetime.now()
