from ..commands.create_support_message_command import CreateSupportMessageCommand
from datetime import datetime

from domain.support import SupportMessage, SupportRepository

class CreateSupportMessageHandler:
    """Handler para criar mensagem de suporte"""
    
    def __init__(self, repository: SupportRepository):
        self.repository = repository
    
    def handle(self, command: CreateSupportMessageCommand) -> SupportMessage:
        """Executa o comando de criar mensagem"""
        
        message = SupportMessage(
            id=None,
            author_id=command.author_id,
            content=command.content,
            timestamp=datetime.now(),
            is_admin_response=command.is_admin_response
        )
        
        return self.repository.create_message(message)