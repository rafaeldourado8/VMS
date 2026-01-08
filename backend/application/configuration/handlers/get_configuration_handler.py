from ..queries.get_configuration_query import GetConfigurationQuery

from domain.configuration import Configuration, ConfigurationRepository

class GetConfigurationHandler:
    """Handler para buscar configuração global"""
    
    def __init__(self, repository: ConfigurationRepository):
        self.repository = repository
    
    def handle(self, query: GetConfigurationQuery) -> Configuration:
        """Executa o use case de buscar configuração"""
        return self.repository.get_global_config()