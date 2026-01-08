from dataclasses import dataclass
from typing import Optional

@dataclass
class UpdateUserCommand:
    """Command para atualizar usuário"""
    
    user_id: int
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None