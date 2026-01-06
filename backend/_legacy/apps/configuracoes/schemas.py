from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class ConfiguracaoGlobalDTO:
    """DTO para exposição e transporte das configurações globais."""
    notificacoes_habilitadas: bool
    email_suporte: Optional[str]
    em_manutencao: bool
    updated_at: datetime

    @classmethod
    def from_model(cls, instance):
        return cls(
            notificacoes_habilitadas=instance.notificacoes_habilitadas,
            email_suporte=instance.email_suporte,
            em_manutencao=instance.em_manutencao,
            updated_at=instance.updated_at
        )