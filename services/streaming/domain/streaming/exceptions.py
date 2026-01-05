class StreamingDomainException(Exception):
    """Exceção base do domínio de streaming"""
    pass


class InvalidStreamPathException(StreamingDomainException):
    """Path de stream inválido"""
    pass


class StreamNotFoundException(StreamingDomainException):
    """Stream não encontrado"""
    pass


class StreamAlreadyExistsException(StreamingDomainException):
    """Stream já existe"""
    pass
