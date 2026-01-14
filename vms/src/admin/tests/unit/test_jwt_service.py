import pytest
from admin.infrastructure.jwt import JWTService


def test_generate_token():
    """Testa geração de token."""
    service = JWTService(secret_key="test_secret")
    
    payload = {
        "user_id": "123",
        "email": "test@test.com",
        "is_admin": False
    }
    
    token = service.generate_token(payload)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token():
    """Testa verificação de token."""
    service = JWTService(secret_key="test_secret")
    
    payload = {
        "user_id": "123",
        "email": "test@test.com"
    }
    
    token = service.generate_token(payload)
    decoded = service.verify_token(token)
    
    assert decoded["user_id"] == "123"
    assert decoded["email"] == "test@test.com"
    assert "exp" in decoded
    assert "iat" in decoded


def test_verify_invalid_token():
    """Testa token inválido."""
    service = JWTService(secret_key="test_secret")
    
    with pytest.raises(ValueError, match="Token inválido"):
        service.verify_token("invalid_token")


def test_verify_token_wrong_secret():
    """Testa token com secret diferente."""
    service1 = JWTService(secret_key="secret1")
    service2 = JWTService(secret_key="secret2")
    
    token = service1.generate_token({"user_id": "123"})
    
    with pytest.raises(ValueError, match="Token inválido"):
        service2.verify_token(token)
