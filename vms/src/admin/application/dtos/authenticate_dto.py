from dataclasses import dataclass


@dataclass
class AuthenticateDTO:
    """DTO para autenticação."""
    email: str
    password: str
