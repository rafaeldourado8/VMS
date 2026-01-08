from dataclasses import dataclass

@dataclass
class CreateSupportMessageCommand:
    """Command para criar mensagem de suporte"""
    
    author_id: int
    content: str
    is_admin_response: bool = False