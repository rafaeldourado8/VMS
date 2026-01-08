from dataclasses import dataclass
from typing import Optional
import re

@dataclass(frozen=True)
class SupportEmail:
    """Value object para email de suporte"""
    
    value: Optional[str]
    
    def __post_init__(self):
        if self.value and not self._is_valid_email(self.value):
            raise ValueError(f"Email de suporte inválido: {self.value}")
    
    def _is_valid_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def __str__(self) -> str:
        return self.value or ""