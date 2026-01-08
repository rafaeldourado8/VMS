import pytest
from infrastructure.persistence.django.repositories.django_configuration_repository import DjangoConfigurationRepository
from domain.configuration import Configuration, SupportEmail


@pytest.mark.django_db
class TestDjangoConfigurationRepository:
    
    def test_get_global_config(self):
        repo = DjangoConfigurationRepository()
        
        config = repo.get_global_config()
        
        assert config is not None
        assert isinstance(config, Configuration)
        assert config.id == 1  # Singleton
    
    def test_save_configuration(self):
        repo = DjangoConfigurationRepository()
        
        # Buscar configuração atual
        config = repo.get_global_config()
        
        # Modificar
        config.enable_maintenance_mode()
        config.update_support_email("test@support.com")
        config.disable_notifications()
        
        # Salvar
        saved_config = repo.save(config)
        
        # Verificar
        assert saved_config.maintenance_mode is True
        assert saved_config.support_email.value == "test@support.com"
        assert saved_config.notifications_enabled is False
        
        # Verificar persistência
        reloaded_config = repo.get_global_config()
        assert reloaded_config.maintenance_mode is True
        assert reloaded_config.support_email.value == "test@support.com"
        assert reloaded_config.notifications_enabled is False
    
    def test_configuration_business_rules(self):
        repo = DjangoConfigurationRepository()
        config = repo.get_global_config()
        
        # Testar regras de negócio
        config.enable_maintenance_mode()
        assert config.is_system_available() is False
        
        config.disable_maintenance_mode()
        assert config.is_system_available() is True
        
        # Testar email de suporte
        config.update_support_email("valid@email.com")
        assert config.support_email.value == "valid@email.com"
        
        # Email inválido deve gerar erro
        with pytest.raises(ValueError):
            config.update_support_email("invalid-email")