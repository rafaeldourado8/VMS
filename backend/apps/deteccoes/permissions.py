# VMS/backend/apps/deteccoes/permissions.py

from django.conf import settings
from rest_framework import permissions


class HasIngestAPIKey(permissions.BasePermission):
    """
    Permite acesso apenas se a API Key de ingestão (do Lambda Injest)
    for fornecida corretamente no header 'X-API-Key'.
    """

    # O nome do header que o Lambda deverá enviar
    HEADER_NAME = "HTTP_X_API_KEY"

    # Mensagem de erro customizada
    message = "API Key de ingestão inválida ou ausente."

    def has_permission(self, request, view):
        # Pega a chave enviada no header
        api_key = request.META.get(self.HEADER_NAME)

        # Pega a chave correta que definimos no settings.py
        correct_key = settings.INGEST_API_KEY

        # Validação:
        # 1. A chave correta DEVE estar configurada no .env
        # 2. A chave enviada não pode ser nula
        # 3. As chaves devem ser iguais

        if not correct_key:
            # Log de segurança: O servidor não está configurado
            print("ALERTA DE SEGURANÇA: INGEST_API_KEY não está definida no .env!")
            return False

        if not api_key:
            return False

        # Compara as chaves
        return api_key == correct_key
