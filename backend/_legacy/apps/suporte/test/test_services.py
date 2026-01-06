import pytest
from apps.suporte.services import SuporteService
from apps.suporte.schemas import CreateMensagemDTO
from apps.suporte.models import Mensagem

@pytest.mark.django_db
class TestSuporteService:
    def test_create_message_admin_flag(self, admin_user):
        """Garante que mensagens enviadas por admin são marcadas como resposta."""
        dto = CreateMensagemDTO(conteudo="Resposta oficial do suporte")
        msg = SuporteService.create_message(admin_user, dto)
        assert msg.respondido_por_admin is True

    def test_list_messages_isolation(self, admin_user, viewer_user):
        """Valida que um viewer não consegue ver mensagens de outros utilizadores."""
        # Admin cria uma mensagem e o viewer cria outra
        SuporteService.create_message(admin_user, CreateMensagemDTO(conteudo="Mensagem Admin"))
        SuporteService.create_message(viewer_user, CreateMensagemDTO(conteudo="Mensagem User"))
        
        # O viewer só deve listar a sua própria mensagem
        viewer_msgs = SuporteService.list_messages(viewer_user)
        assert viewer_msgs.count() == 1
        assert viewer_msgs.first().autor == viewer_user