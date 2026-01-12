class DetectionDomainException(Exception):
    """Exceção base do domínio de detecção"""
    pass



class InvalidBoundingBoxException(DetectionDomainException):
    """Bounding box inválido"""
    pass


class VehicleNotFoundException(DetectionDomainException):
    """Veículo não encontrado"""
    pass
