from .configuration_mapper import ConfigurationMapper

from apps.configuracoes.models import ConfiguracaoGlobal
from domain.configuration import Configuration, ConfigurationRepository

class DjangoConfigurationRepository(ConfigurationRepository):
    """Implementação Django do repositório de configurações"""
    
    def get_global_config(self) -> Configuration:
        """Busca configuração global (singleton)"""
        model = ConfiguracaoGlobal.load()
        return ConfigurationMapper.to_domain(model)
    
    def save(self, config: Configuration) -> Configuration:
        """Salva configuração global"""
        model = ConfiguracaoGlobal.load()
        model = ConfigurationMapper.to_model(config, model)
        model.save()
        return ConfigurationMapper.to_domain(model)