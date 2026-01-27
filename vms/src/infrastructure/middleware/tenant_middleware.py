import logging
from uuid import UUID
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from infrastructure.repositories import DjangoCityRepository

logger = logging.getLogger(__name__)

class TenantMiddleware(MiddlewareMixin):
    
    PUBLIC_PATHS = [
        '/admin/',
        '/static/',
        '/health/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.city_repo = DjangoCityRepository()
    
    def process_request(self, request):
        # Ignora rotas públicas
        if any(request.path.startswith(path) for path in self.PUBLIC_PATHS):
            return None
        
        # Superadmin bypassa validação
        if request.user.is_authenticated and request.user.is_superuser:
            logger.info(f"SUPERADMIN access: {request.user.username}")
            return None
        
        # Extrai city_id do header
        city_id_header = request.headers.get('X-City-ID')
        
        if not city_id_header:
            logger.warning(f"Missing X-City-ID header: {request.path}")
            return JsonResponse({'error': 'X-City-ID header required'}, status=400)
        
        # Valida UUID
        try:
            city_id = UUID(city_id_header)
        except ValueError:
            logger.warning(f"Invalid X-City-ID format: {city_id_header}")
            return JsonResponse({'error': 'Invalid X-City-ID format'}, status=400)
        
        # Valida se cidade existe
        if not self.city_repo.exists(city_id):
            logger.warning(f"City not found: {city_id}")
            return JsonResponse({'error': 'City not found'}, status=404)
        
        # Injeta city_id no request
        request.city_id = city_id
        
        logger.info(f"Tenant resolved: {city_id} | Path: {request.path}")
        
        return None
