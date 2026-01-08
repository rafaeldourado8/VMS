import pytest
from django.contrib.auth import get_user_model
from infrastructure.persistence.django.repositories.django_user_repository import DjangoUserRepository
from domain.user import User, Email, Username, UserRole

User_Model = get_user_model()


@pytest.mark.django_db
class TestDjangoUserRepository:
    
    def test_save_new_user(self):
        repo = DjangoUserRepository()
        
        user = User(
            id=None,
            email=Email("test@test.com"),
            name=Username("Test User"),
            role=UserRole.VIEWER
        )
        
        saved = repo.save(user)
        
        assert saved.id is not None
        assert saved.email.value == "test@test.com"
        assert saved.name.value == "Test User"
        assert saved.role == UserRole.VIEWER
    
    def test_find_by_id(self):
        repo = DjangoUserRepository()
        
        user = User(
            id=None,
            email=Email("find@test.com"),
            name=Username("Find User"),
            role=UserRole.ADMIN
        )
        saved = repo.save(user)
        
        found = repo.find_by_id(saved.id)
        
        assert found is not None
        assert found.email.value == "find@test.com"
        assert found.role == UserRole.ADMIN
    
    def test_find_by_email(self):
        repo = DjangoUserRepository()
        
        user = User(
            id=None,
            email=Email("email@test.com"),
            name=Username("Email User"),
            role=UserRole.VIEWER
        )
        repo.save(user)
        
        found = repo.find_by_email(Email("email@test.com"))
        
        assert found is not None
        assert found.name.value == "Email User"
    
    def test_exists_by_email(self):
        repo = DjangoUserRepository()
        
        user = User(
            id=None,
            email=Email("exists@test.com"),
            name=Username("Exists User"),
            role=UserRole.VIEWER
        )
        repo.save(user)
        
        assert repo.exists_by_email(Email("exists@test.com")) is True
        assert repo.exists_by_email(Email("notexists@test.com")) is False
    
    def test_find_all_active(self):
        repo = DjangoUserRepository()
        
        # Criar usuário ativo
        active_user = User(
            id=None,
            email=Email("active@test.com"),
            name=Username("Active User"),
            role=UserRole.VIEWER,
            is_active=True
        )
        repo.save(active_user)
        
        # Criar usuário inativo
        inactive_user = User(
            id=None,
            email=Email("inactive@test.com"),
            name=Username("Inactive User"),
            role=UserRole.VIEWER,
            is_active=False
        )
        repo.save(inactive_user)
        
        active_users = repo.find_all_active()
        
        assert len(active_users) >= 1
        assert all(user.is_active for user in active_users)
    
    def test_delete_user(self):
        repo = DjangoUserRepository()
        
        user = User(
            id=None,
            email=Email("delete@test.com"),
            name=Username("Delete User"),
            role=UserRole.VIEWER
        )
        saved = repo.save(user)
        
        repo.delete(saved.id)
        
        found = repo.find_by_id(saved.id)
        assert found is None