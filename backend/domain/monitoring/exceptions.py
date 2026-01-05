class MonitoringDomainException(Exception):
    """Exceção base do domínio de monitoramento"""
    pass


class InvalidStreamUrlException(MonitoringDomainException):
    """URL de stream inválida"""
    pass


class InvalidCoordinatesException(MonitoringDomainException):
    """Coordenadas geográficas inválidas"""
    pass


class CameraNotFoundException(MonitoringDomainException):
    """Câmera não encontrada"""
    pass
