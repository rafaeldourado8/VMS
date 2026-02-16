from django.utils.deprecation import MiddlewareMixin
from .models import TenantIsolation

class TenantIsolationMiddleware(MiddlewareMixin):
    """Middleware para isolamento de dados por usuário"""
    
    def process_request(self, request):
        if request.user.is_authenticated:
            request.tenant_user = request.user
        return None

def get_user_resources(user, resource_type, permission='read'):
    """Retorna IDs de recursos que o usuário tem acesso"""
    if user.is_staff or user.role == 'admin':
        return None  # Admin tem acesso a tudo
    
    permission_field = f'can_{permission}'
    isolations = TenantIsolation.objects.filter(
        user=user,
        resource_type=resource_type,
        **{permission_field: True}
    )
    return [iso.resource_id for iso in isolations]

def check_user_permission(user, resource_type, resource_id, permission='read'):
    """Verifica se usuário tem permissão específica em um recurso"""
    if user.is_staff or user.role == 'admin':
        return True
    
    permission_field = f'can_{permission}'
    return TenantIsolation.objects.filter(
        user=user,
        resource_type=resource_type,
        resource_id=resource_id,
        **{permission_field: True}
    ).exists()

def grant_user_access(user, resource_type, resource_id, read=True, write=False, delete=False):
    """Concede acesso a um recurso para um usuário"""
    TenantIsolation.objects.update_or_create(
        user=user,
        resource_type=resource_type,
        resource_id=resource_id,
        defaults={
            'can_read': read,
            'can_write': write,
            'can_delete': delete,
        }
    )
