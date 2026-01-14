from dataclasses import dataclass


@dataclass
class CreateUserDTO:
    """DTO para criação de usuário."""
    email: str
    name: str
    password: str
    city_ids: list[str]
    is_admin: bool = False
