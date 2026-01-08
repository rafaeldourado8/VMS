from dataclasses import dataclass

@dataclass
class GetConfigurationQuery:
    """Query para buscar configuração global"""
    pass  # Singleton, não precisa de parâmetros