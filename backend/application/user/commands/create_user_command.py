from dataclasses import dataclass
from typing import Optional

@dataclass
class CreateUserCommand:
    """Command para criar usuário"""
    
    email: str
    name: str
    password: str
    role: str = "viewer"
    is_staff: bool = False