from django.db import models
from .middleware import get_user_resources, check_user_permission

class TenantAwareQuerySet(models.QuerySet):
    """QuerySet que filtra automaticamente por tenant"""
    
    def for_user(self, user, resource_type):
        """Filtra recursos que o usuário tem acesso"""
        if user.is_staff or user.role == 'admin':
            return self
        
        resource_ids = get_user_resources(user, resource_type, 'read')
        if resource_ids is None:
            return self
        
        return self.filter(id__in=resource_ids)

class TenantAwareManager(models.Manager):
    """Manager que usa TenantAwareQuerySet"""
    
    def get_queryset(self):
        return TenantAwareQuerySet(self.model, using=self._db)
    
    def for_user(self, user, resource_type):
        return self.get_queryset().for_user(user, resource_type)

class TenantAwareMixin:
    """Mixin para adicionar isolamento de tenant aos models"""
    
    @classmethod
    def get_resource_type(cls):
        """Retorna o tipo de recurso (deve ser sobrescrito)"""
        return cls.__name__.lower()
    
    def grant_access_to_user(self, user, read=True, write=False, delete=False):
        """Concede acesso a este recurso para um usuário"""
        from .middleware import grant_user_access
        grant_user_access(
            user=user,
            resource_type=self.get_resource_type(),
            resource_id=self.id,
            read=read,
            write=write,
            delete=delete
        )
    
    def user_can_access(self, user, permission='read'):
        """Verifica se usuário tem acesso a este recurso"""
        return check_user_permission(
            user=user,
            resource_type=self.get_resource_type(),
            resource_id=self.id,
            permission=permission
        )
