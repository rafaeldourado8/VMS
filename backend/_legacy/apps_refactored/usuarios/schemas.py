from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class UsuarioDTO:
    """Objeto de transferência de dados para Utilizadores."""
    email: str
    name: str
    role: str
    id: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    password: Optional[str] = field(default=None, repr=False)

    @classmethod
    def from_model(cls, user):
        """Converte uma instância do Model para DTO."""
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )