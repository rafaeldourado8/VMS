from dataclasses import dataclass

@dataclass
class DeleteUserCommand:
    """Command para deletar usuário"""
    
    user_id: int