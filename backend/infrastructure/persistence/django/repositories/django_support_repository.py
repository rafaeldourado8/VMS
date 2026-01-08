from .support_message_mapper import SupportMessageMapper
from typing import List, Optional

from apps.suporte.models import Mensagem
from domain.support import SupportMessage, SupportRepository

class DjangoSupportRepository(SupportRepository):
    """Implementação Django do repositório de suporte"""
    
    def create_message(self, message: SupportMessage) -> SupportMessage:
        """Cria uma nova mensagem de suporte"""
        model = SupportMessageMapper.to_model(message)
        model.save()
        return SupportMessageMapper.to_domain(model)
    
    def get_messages_by_user(self, user_id: int) -> List[SupportMessage]:
        """Busca mensagens de um usuário"""
        models = Mensagem.objects.filter(autor_id=user_id).order_by('-timestamp')
        return [SupportMessageMapper.to_domain(model) for model in models]
    
    def get_all_messages(self) -> List[SupportMessage]:
        """Busca todas as mensagens (admin)"""
        models = Mensagem.objects.all().order_by('-timestamp')
        return [SupportMessageMapper.to_domain(model) for model in models]
    
    def get_message_by_id(self, message_id: int) -> Optional[SupportMessage]:
        """Busca mensagem por ID"""
        try:
            model = Mensagem.objects.get(id=message_id)
            return SupportMessageMapper.to_domain(model)
        except Mensagem.DoesNotExist:
            return None