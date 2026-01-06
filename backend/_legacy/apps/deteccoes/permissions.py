from django.conf import settings
from rest_framework import permissions

class HasIngestAPIKey(permissions.BasePermission):
    """
    Permite acesso apenas se a API Key correta for fornecida no header 'X-API-Key'.
    Essencial para a segurança do endpoint de ingestão.
    """
    HEADER_NAME = "HTTP_X_API_KEY"
    message = "API Key de ingestão inválida ou ausente."

    def has_permission(self, request, view):
        api_key = request.META.get(self.HEADER_NAME)
        correct_key = getattr(settings, 'INGEST_API_KEY', None)

        if not correct_key:
            # Alerta caso a configuração no .env esteja em falta
            return False

        return api_key == correct_key