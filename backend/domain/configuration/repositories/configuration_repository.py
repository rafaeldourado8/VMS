from ..entities.configuration import Configuration
from abc import ABC, abstractmethod

class ConfigurationRepository(ABC):
    """Interface de repositório para Configuration"""
    
    @abstractmethod
    def get_global_config(self) -> Configuration:
        """Busca configuração global (singleton)"""
        pass
    
    @abstractmethod
    def save(self, config: Configuration) -> Configuration:
        """Salva configuração global"""
        pass