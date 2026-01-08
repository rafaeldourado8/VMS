class DetectionDomainException(Exception):
    """Exceção base do domínio de detecção"""
    pass

class InvalidLicensePlateException(DetectionDomainException):
    """Placa de veículo inválida"""
    pass

class InvalidConfidenceException(DetectionDomainException):
    """Confiança inválida (deve estar entre 0.0 e 1.0)"""
    pass

class DetectionNotFoundException(DetectionDomainException):
    """Detecção não encontrada"""
    pass
