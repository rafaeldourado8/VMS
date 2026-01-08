from apps.suporte.models import Mensagem
from domain.support.entities.support_message import SupportMessage

class SupportMessageMapper:
    """Mapper entre domínio e modelo Django para Support"""
    
    @staticmethod
    def to_domain(model: Mensagem) -> SupportMessage:
        """Converte modelo Django para entidade de domínio"""
        return SupportMessage(
            id=model.id,
            author_id=model.autor_id,
            content=model.conteudo,
            timestamp=model.timestamp,
            is_admin_response=model.respondido_por_admin
        )
    
    @staticmethod
    def to_model(entity: SupportMessage) -> Mensagem:
        """Converte entidade de domínio para modelo Django"""
        return Mensagem(
            id=entity.id,
            autor_id=entity.author_id,
            conteudo=entity.content,
            timestamp=entity.timestamp,
            respondido_por_admin=entity.is_admin_response
        )