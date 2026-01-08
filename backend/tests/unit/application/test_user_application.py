import pytest
from unittest.mock import Mock
from domain.user import User, Email, Username, UserRole, UserRepository
from domain.user.exceptions import UserAlreadyExistsException, UserNotFoundException
from application.user import (
    CreateUserCommand, CreateUserHandler,
    GetUserQuery, GetUserHandler,
    UserPermissions
)


class TestUserApplication:
    
    def test_create_user_handler(self):
        # Mock repository
        mock_repo = Mock(spec=UserRepository)
        mock_repo.exists_by_email.return_value = False
        mock_repo.save.return_value = User(
            id=1,
            email=Email("test@test.com"),
            name=Username("Test User"),
            role=UserRole.VIEWER
        )
        
        # Handler
        handler = CreateUserHandler(mock_repo)
        command = CreateUserCommand(
            email="test@test.com",
            name="Test User",
            password="password123"
        )
        
        # Execute
        result = handler.handle(command)
        
        # Verify
        assert result.id == 1
        assert result.email.value == "test@test.com"
        assert result.name.value == "Test User"
        mock_repo.exists_by_email.assert_called_once()
        mock_repo.save.assert_called_once()
    
    def test_create_user_already_exists(self):
        # Mock repository
        mock_repo = Mock(spec=UserRepository)
        mock_repo.exists_by_email.return_value = True
        
        # Handler
        handler = CreateUserHandler(mock_repo)
        command = CreateUserCommand(
            email="existing@test.com",
            name="Existing User",
            password="password123"
        )
        
        # Execute and verify exception
        with pytest.raises(UserAlreadyExistsException):
            handler.handle(command)
    
    def test_get_user_handler(self):
        # Mock repository
        mock_repo = Mock(spec=UserRepository)
        mock_repo.find_by_id.return_value = User(
            id=1,
            email=Email("test@test.com"),
            name=Username("Test User"),
            role=UserRole.VIEWER
        )
        
        # Handler
        handler = GetUserHandler(mock_repo)
        query = GetUserQuery(user_id=1)
        
        # Execute
        result = handler.handle(query)
        
        # Verify
        assert result.id == 1
        assert result.email.value == "test@test.com"
        mock_repo.find_by_id.assert_called_once_with(1)
    
    def test_get_user_not_found(self):
        # Mock repository
        mock_repo = Mock(spec=UserRepository)
        mock_repo.find_by_id.return_value = None
        
        # Handler
        handler = GetUserHandler(mock_repo)
        query = GetUserQuery(user_id=999)
        
        # Execute and verify exception
        with pytest.raises(UserNotFoundException):
            handler.handle(query)
    
    def test_user_permissions(self):
        # Admin user
        admin = User(
            id=1,
            email=Email("admin@test.com"),
            name=Username("Admin"),
            role=UserRole.ADMIN,
            is_active=True,
            is_staff=True
        )
        
        # Regular user
        user = User(
            id=2,
            email=Email("user@test.com"),
            name=Username("User"),
            role=UserRole.VIEWER,
            is_active=True
        )
        
        # Admin permissions
        assert UserPermissions.can_create_user(admin) is True
        assert UserPermissions.can_update_user(admin, user) is True
        assert UserPermissions.can_delete_user(admin, user) is True
        assert UserPermissions.can_list_users(admin) is True
        
        # Regular user permissions
        assert UserPermissions.can_create_user(user) is False
        assert UserPermissions.can_update_user(user, user) is True  # Can update self
        assert UserPermissions.can_update_user(user, admin) is False  # Cannot update others
        assert UserPermissions.can_delete_user(user, admin) is False
        assert UserPermissions.can_list_users(user) is False