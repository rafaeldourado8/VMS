import pytest
from admin.application import CreateUserUseCase, CreateUserDTO


def test_create_user_success(user_repository):
    """Testa criação de usuário com sucesso."""
    use_case = CreateUserUseCase(user_repository)
    
    dto = CreateUserDTO(
        email="user@test.com",
        name="Test User",
        password="password123",
        city_ids=["city1"],
        is_admin=False
    )
    
    user = use_case.execute(dto)
    
    assert user.email == "user@test.com"
    assert user.name == "Test User"
    assert user.city_ids == ["city1"]
    assert user.is_admin is False
    assert user.password_hash != "password123"  # Deve estar hasheado


def test_create_user_duplicate_email(user_repository):
    """Testa erro ao criar usuário com email duplicado."""
    use_case = CreateUserUseCase(user_repository)
    
    dto = CreateUserDTO(
        email="user@test.com",
        name="Test User",
        password="password123",
        city_ids=["city1"]
    )
    
    use_case.execute(dto)
    
    # Tenta criar novamente com mesmo email
    with pytest.raises(ValueError, match="já está em uso"):
        use_case.execute(dto)


def test_create_admin_user(user_repository):
    """Testa criação de usuário admin."""
    use_case = CreateUserUseCase(user_repository)
    
    dto = CreateUserDTO(
        email="admin@test.com",
        name="Admin User",
        password="admin123",
        city_ids=[],
        is_admin=True
    )
    
    user = use_case.execute(dto)
    
    assert user.is_admin is True
