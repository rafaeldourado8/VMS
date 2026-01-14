import pytest
from admin.application import (
    CreateUserUseCase,
    AuthenticateUserUseCase,
    CreateUserDTO,
    AuthenticateDTO
)


def test_authenticate_user_success(user_repository, jwt_service):
    """Testa autenticação com sucesso."""
    # Cria usuário
    create_use_case = CreateUserUseCase(user_repository)
    dto = CreateUserDTO(
        email="user@test.com",
        name="Test User",
        password="password123",
        city_ids=["city1"]
    )
    user = create_use_case.execute(dto)
    
    # Autentica
    auth_use_case = AuthenticateUserUseCase(user_repository, jwt_service)
    auth_dto = AuthenticateDTO(
        email="user@test.com",
        password="password123"
    )
    
    result = auth_use_case.execute(auth_dto)
    
    assert "token" in result
    assert result["token"] == f"token_{user.id}"
    assert result["user"]["email"] == "user@test.com"
    assert result["user"]["name"] == "Test User"


def test_authenticate_user_invalid_email(user_repository, jwt_service):
    """Testa autenticação com email inválido."""
    auth_use_case = AuthenticateUserUseCase(user_repository, jwt_service)
    auth_dto = AuthenticateDTO(
        email="invalid@test.com",
        password="password123"
    )
    
    with pytest.raises(ValueError, match="Credenciais inválidas"):
        auth_use_case.execute(auth_dto)


def test_authenticate_user_invalid_password(user_repository, jwt_service):
    """Testa autenticação com senha inválida."""
    # Cria usuário
    create_use_case = CreateUserUseCase(user_repository)
    dto = CreateUserDTO(
        email="user@test.com",
        name="Test User",
        password="password123",
        city_ids=["city1"]
    )
    create_use_case.execute(dto)
    
    # Tenta autenticar com senha errada
    auth_use_case = AuthenticateUserUseCase(user_repository, jwt_service)
    auth_dto = AuthenticateDTO(
        email="user@test.com",
        password="wrong_password"
    )
    
    with pytest.raises(ValueError, match="Credenciais inválidas"):
        auth_use_case.execute(auth_dto)


def test_authenticate_inactive_user(user_repository, jwt_service):
    """Testa autenticação de usuário inativo."""
    # Cria usuário
    create_use_case = CreateUserUseCase(user_repository)
    dto = CreateUserDTO(
        email="user@test.com",
        name="Test User",
        password="password123",
        city_ids=["city1"]
    )
    user = create_use_case.execute(dto)
    
    # Desativa usuário
    user.deactivate()
    user_repository.save(user)
    
    # Tenta autenticar
    auth_use_case = AuthenticateUserUseCase(user_repository, jwt_service)
    auth_dto = AuthenticateDTO(
        email="user@test.com",
        password="password123"
    )
    
    with pytest.raises(ValueError, match="Usuário inativo"):
        auth_use_case.execute(auth_dto)
