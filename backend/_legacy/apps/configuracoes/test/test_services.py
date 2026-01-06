import pytest
from apps.configuracoes.services import ConfiguracaoGlobalService

@pytest.mark.django_db
class TestConfiguracaoService:
    def test_singleton_persistence(self):
        """Valida se o Singleton e o DTO funcionam sem erros de BD."""
        dto = ConfiguracaoGlobalService.get_settings_dto()
        assert dto is not None

    def test_partial_update(self):
        """Valida a atualização atómica de campos."""
        ConfiguracaoGlobalService.update_settings({"email_suporte": "suporte@vms.com"})
        updated = ConfiguracaoGlobalService.update_settings({"em_manutencao": True})
        assert updated.email_suporte == "suporte@vms.com"
        assert updated.em_manutencao is True