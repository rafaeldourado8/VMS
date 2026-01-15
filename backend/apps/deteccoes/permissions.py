from django.conf import settings
from rest_framework import permissions

class HasIngestAPIKey(permissions.BasePermission):
    """
    Permite acesso apenas se a API Key correta for fornecida no header 'X-API-Key'.
    Essencial para a segurança do endpoint de ingestão.
    """
    message = "API Key de ingestão inválida ou ausente."

    def has_permission(self, request, view):
        # Tenta ambos os headers para compatibilidade
        api_key = request.META.get('HTTP_X_API_KEY') or request.META.get('HTTP_AUTHORIZATION', '').replace('Api-Key ', '')
        correct_key = getattr(settings, 'ADMIN_API_KEY', None)

        if not correct_key:
            return False

        return api_key == correct_key