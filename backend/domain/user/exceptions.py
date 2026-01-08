class UserDomainException(Exception):
    """Exceção base do domínio de usuários"""
    pass

class UserNotFoundException(UserDomainException):
    """Usuário não encontrado"""
    pass

class UserAlreadyExistsException(UserDomainException):
    """Usuário já existe"""
    pass

class InvalidCredentialsException(UserDomainException):
    """Credenciais inválidas"""
    pass

class InsufficientPermissionsException(UserDomainException):
    """Permissões insuficientes"""
    pass