import pytest
from admin.domain import User, IUserRepository


class InMemoryUserRepository(IUserRepository):
    """Repositório em memória para testes."""
    
    def __init__(self):
        self._users: dict[str, User] = {}
    
    def save(self, user: User) -> User:
        self._users[user.id] = user
        return user
    
    def find_by_id(self, user_id: str) -> User | None:
        return self._users.get(user_id)
    
    def find_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None
    
    def find_all(self) -> list[User]:
        return list(self._users.values())
    
    def delete(self, user_id: str) -> None:
        if user_id in self._users:
            del self._users[user_id]
    
    def exists_by_email(self, email: str) -> bool:
        return self.find_by_email(email) is not None


class MockJWTService:
    """Mock do serviço JWT."""
    
    def generate_token(self, payload: dict) -> str:
        return f"token_{payload['user_id']}"


@pytest.fixture
def user_repository():
    return InMemoryUserRepository()


@pytest.fixture
def jwt_service():
    return MockJWTService()
