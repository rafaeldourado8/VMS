from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Email:
    """Value object para email"""
    
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Email não pode ser vazio")
        
        if not self._is_valid_email(self.value):
            raise ValueError(f"Email inválido: {self.value}")
    
    def _is_valid_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def __str__(self) -> str:
        return self.value