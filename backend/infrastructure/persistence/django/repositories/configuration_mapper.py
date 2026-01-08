from typing import Optional

from apps.configuracoes.models import ConfiguracaoGlobal
from domain.configuration import Configuration, SupportEmail

class ConfigurationMapper:
    """Mapper entre entidade Configuration e modelo Django"""
    
    @staticmethod
    def to_domain(model: ConfiguracaoGlobal) -> Configuration:
        """Converte modelo Django para entidade Configuration"""
        return Configuration(
            id=model.id,
            notifications_enabled=model.notificacoes_habilitadas,
            support_email=SupportEmail(model.email_suporte),
            maintenance_mode=model.em_manutencao,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    @staticmethod
    def to_model(config: Configuration, model: Optional[ConfiguracaoGlobal] = None) -> ConfiguracaoGlobal:
        """Converte entidade Configuration para modelo Django"""
        if model is None:
            model = ConfiguracaoGlobal()
        
        model.notificacoes_habilitadas = config.notifications_enabled
        model.email_suporte = config.support_email.value
        model.em_manutencao = config.maintenance_mode
        
        return model