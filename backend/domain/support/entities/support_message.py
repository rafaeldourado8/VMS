from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class SupportMessage:
    """Entidade de domínio para mensagens de suporte"""
    
    id: Optional[int]
    author_id: int
    content: str
    timestamp: datetime
    is_admin_response: bool = False
    
    def __post_init__(self):
        if not self.content.strip():
            raise ValueError("Conteúdo da mensagem não pode estar vazio")
        
        if len(self.content) > 5000:
            raise ValueError("Mensagem muito longa (máximo 5000 caracteres)")
    
    def is_from_admin(self) -> bool:
        """Verifica se a mensagem é de um administrador"""
        return self.is_admin_response