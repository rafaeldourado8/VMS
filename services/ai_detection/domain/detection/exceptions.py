class DetectionDomainException(Exception):
    """Exceção base do domínio de detecção"""
    pass


class InvalidPointException(DetectionDomainException):
    """Ponto inválido"""
    pass


class InvalidPolygonException(DetectionDomainException):
    """Polígono inválido"""
    pass


class InvalidBoundingBoxException(DetectionDomainException):
    """Bounding box inválido"""
    pass


class VehicleNotFoundException(DetectionDomainException):
    """Veículo não encontrado"""
    pass
