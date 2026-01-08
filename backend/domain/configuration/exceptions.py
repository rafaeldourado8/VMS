class ConfigurationDomainException(Exception):
    """Exceção base do domínio de configurações"""
    pass

class ConfigurationNotFoundException(ConfigurationDomainException):
    """Configuração não encontrada"""
    pass

class InvalidConfigurationException(ConfigurationDomainException):
    """Configuração inválida"""
    pass