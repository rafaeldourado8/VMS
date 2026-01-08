import pytest
from domain.user import User, Email, Username, Password, UserRole
from domain.user.exceptions import UserDomainException


class TestUserDomain:
    
    def test_create_user_with_valid_data(self):
        email = Email("test@example.com")
        name = Username("Test User")
        
        user = User(
            id=None,
            email=email,
            name=name,
            role=UserRole.VIEWER
        )
        
        assert user.email.value == "test@example.com"
        assert user.name.value == "Test User"
        assert user.role == UserRole.VIEWER
        assert user.is_active is True
        assert user.is_staff is False
    
    def test_email_validation(self):
        with pytest.raises(ValueError):
            Email("")
        
        with pytest.raises(ValueError):
            Email("invalid-email")
        
        # Email válido não deve gerar erro
        email = Email("valid@example.com")
        assert email.value == "valid@example.com"
    
    def test_username_validation(self):
        with pytest.raises(ValueError):
            Username("")
        
        with pytest.raises(ValueError):
            Username("a")  # Muito curto
        
        with pytest.raises(ValueError):
            Username("a" * 151)  # Muito longo
        
        # Nome válido não deve gerar erro
        name = Username("Valid Name")
        assert name.value == "Valid Name"
    
    def test_user_role_management(self):
        user = User(
            id=1,
            email=Email("admin@example.com"),
            name=Username("Admin User")
        )
        
        # Inicialmente é viewer
        assert user.role == UserRole.VIEWER
        assert not user.is_admin()
        assert not user.can_manage_users()
        
        # Tornar admin
        user.make_admin()
        assert user.role == UserRole.ADMIN
        assert user.is_admin()
        assert user.can_manage_users()
        assert user.is_staff is True
        
        # Voltar para viewer
        user.make_viewer()
        assert user.role == UserRole.VIEWER
        assert not user.is_admin()
        assert not user.can_manage_users()
        assert user.is_staff is False
    
    def test_user_activation(self):
        user = User(
            id=1,
            email=Email("user@example.com"),
            name=Username("Test User")
        )
        
        # Inicialmente ativo
        assert user.is_active is True
        assert user.can_access_cameras() is True
        
        # Desativar
        user.deactivate()
        assert user.is_active is False
        assert user.can_access_cameras() is False
        
        # Reativar
        user.activate()
        assert user.is_active is True
        assert user.can_access_cameras() is True
    
    def test_password_security(self):
        password = Password("hashed_password_123")
        
        # Senha nunca deve ser exposta
        assert str(password) == "***"
        assert password.hashed_value == "hashed_password_123"