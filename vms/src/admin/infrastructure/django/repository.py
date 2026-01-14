from typing import Optional
from admin.domain import User, IUserRepository
from .models import UserModel


class DjangoUserRepository(IUserRepository):
    """Repositório Django para User."""
    
    def save(self, user: User) -> User:
        UserModel.objects.update_or_create(
            id=user.id,
            defaults={
                "email": user.email,
                "name": user.name,
                "password_hash": user.password_hash,
                "city_ids": user.city_ids,
                "is_admin": user.is_admin,
                "is_active": user.is_active
            }
        )
        return user
    
    def find_by_id(self, user_id: str) -> Optional[User]:
        try:
            model = UserModel.objects.get(id=user_id)
            return self._to_entity(model)
        except UserModel.DoesNotExist:
            return None
    
    def find_by_email(self, email: str) -> Optional[User]:
        try:
            model = UserModel.objects.get(email=email)
            return self._to_entity(model)
        except UserModel.DoesNotExist:
            return None
    
    def find_all(self) -> list[User]:
        return [self._to_entity(m) for m in UserModel.objects.all()]
    
    def delete(self, user_id: str) -> None:
        UserModel.objects.filter(id=user_id).delete()
    
    def exists_by_email(self, email: str) -> bool:
        return UserModel.objects.filter(email=email).exists()
    
    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            name=model.name,
            password_hash=model.password_hash,
            city_ids=model.city_ids,
            is_admin=model.is_admin,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
