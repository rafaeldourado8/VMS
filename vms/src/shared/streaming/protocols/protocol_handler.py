from abc import ABC, abstractmethod

class ProtocolHandler(ABC):
    
    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """Valida se a URL é válida para o protocolo."""
        pass
    
    @abstractmethod
    def normalize_url(self, url: str) -> str:
        """Normaliza a URL para o formato esperado."""
        pass
    
    @abstractmethod
    def get_protocol_name(self) -> str:
        """Retorna o nome do protocolo."""
        pass
