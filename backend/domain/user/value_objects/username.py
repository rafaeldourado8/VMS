from dataclasses import dataclass

@dataclass(frozen=True)
class Username:
    """Value object para nome de usuário"""
    
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Nome de usuário não pode ser vazio")
        
        if len(self.value) < 2:
            raise ValueError("Nome de usuário deve ter pelo menos 2 caracteres")
        
        if len(self.value) > 150:
            raise ValueError("Nome de usuário deve ter no máximo 150 caracteres")
    
    def __str__(self) -> str:
        return self.value