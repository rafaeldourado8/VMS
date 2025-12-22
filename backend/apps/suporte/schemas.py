from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class MensagemDTO:
    """DTO para exposição de mensagens de suporte."""
    id: int
    autor_id: int
    autor_email: str
    conteudo: str
    timestamp: datetime
    respondido_por_admin: bool

    @classmethod
    def from_model(cls, instance):
        return cls(
            id=instance.id,
            autor_id=instance.autor.id,
            autor_email=instance.autor.email,
            conteudo=instance.conteudo,
            timestamp=instance.timestamp,
            respondido_por_admin=instance.respondido_por_admin
        )

@dataclass(frozen=True)
class CreateMensagemDTO:
    """DTO para criação de uma nova mensagem."""
    conteudo: str