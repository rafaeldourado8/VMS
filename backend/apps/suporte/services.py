from .models import Mensagem
from .schemas import CreateMensagemDTO
import logging

from django.db import transaction

logger = logging.getLogger(__name__)

class SuporteService:
    """Serviço para gestão do chat de suporte."""

    @staticmethod
    def list_messages(user):
        """
        Lista mensagens baseadas na role:
        - Admin vê tudo.
        - Viewer vê apenas as suas.
        """
        if user.role == "admin":
            return Mensagem.objects.all().order_by("autor__email", "-timestamp")
        return Mensagem.objects.filter(autor=user).order_by("-timestamp")

    @staticmethod
    def create_message(user, data: CreateMensagemDTO) -> Mensagem:
        """Cria mensagem e define automaticamente se é resposta de admin."""
        with transaction.atomic():
            mensagem = Mensagem.objects.create(
                autor=user,
                conteudo=data.conteudo,
                respondido_por_admin=(user.role == "admin")
            )
        
        logger.info(f"Mensagem de suporte criada por {user.email} (Admin: {mensagem.respondido_por_admin})")
        return mensagem