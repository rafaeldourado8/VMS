from django.utils.deprecation import MiddlewareMixin
from apps.tenants.models import Organization

class TenantMiddleware(MiddlewareMixin):
    """Detecta organização atual baseado no usuário autenticado"""
    
    def process_request(self, request):
        request.tenant = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            if hasattr(request.user, 'organization') and request.user.organization:
                request.tenant = request.user.organization
