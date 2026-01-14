import pytest
from datetime import datetime
from admin.domain import User


def test_create_user():
    """Testa criação de usuário."""
    user = User(
        id="1",
        email="user@test.com",
        name="Test User",
        password_hash="hash123",
        city_ids=["city1"],
        is_admin=False
    )
    
    assert user.id == "1"
    assert user.email == "user@test.com"
    assert user.name == "Test User"
    assert user.city_ids == ["city1"]
    assert user.is_admin is False
    assert user.is_active is True


def test_user_invalid_email():
    """Testa validação de email."""
    with pytest.raises(ValueError, match="Email inválido"):
        User(
            id="1",
            email="invalid",
            name="Test",
            password_hash="hash"
        )


def test_user_invalid_name():
    """Testa validação de nome."""
    with pytest.raises(ValueError, match="Nome deve ter no mínimo 3 caracteres"):
        User(
            id="1",
            email="test@test.com",
            name="ab",
            password_hash="hash"
        )


def test_can_access_city():
    """Testa verificação de acesso a cidade."""
    user = User(
        id="1",
        email="user@test.com",
        name="Test User",
        password_hash="hash",
        city_ids=["city1", "city2"]
    )
    
    assert user.can_access_city("city1") is True
    assert user.can_access_city("city3") is False


def test_admin_can_access_any_city():
    """Testa que admin pode acessar qualquer cidade."""
    user = User(
        id="1",
        email="admin@test.com",
        name="Admin",
        password_hash="hash",
        is_admin=True
    )
    
    assert user.can_access_city("any_city") is True


def test_add_city_access():
    """Testa adição de acesso a cidade."""
    user = User(
        id="1",
        email="user@test.com",
        name="Test User",
        password_hash="hash",
        city_ids=["city1"]
    )
    
    user.add_city_access("city2")
    
    assert "city2" in user.city_ids
    assert user.updated_at is not None


def test_remove_city_access():
    """Testa remoção de acesso a cidade."""
    user = User(
        id="1",
        email="user@test.com",
        name="Test User",
        password_hash="hash",
        city_ids=["city1", "city2"]
    )
    
    user.remove_city_access("city1")
    
    assert "city1" not in user.city_ids
    assert user.updated_at is not None


def test_deactivate_user():
    """Testa desativação de usuário."""
    user = User(
        id="1",
        email="user@test.com",
        name="Test User",
        password_hash="hash"
    )
    
    user.deactivate()
    
    assert user.is_active is False
    assert user.updated_at is not None


def test_activate_user():
    """Testa ativação de usuário."""
    user = User(
        id="1",
        email="user@test.com",
        name="Test User",
        password_hash="hash",
        is_active=False
    )
    
    user.activate()
    
    assert user.is_active is True
    assert user.updated_at is not None
