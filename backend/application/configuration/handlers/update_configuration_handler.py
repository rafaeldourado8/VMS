from ..commands.update_configuration_command import UpdateConfigurationCommand

from domain.configuration import Configuration, ConfigurationRepository

class UpdateConfigurationHandler:
    """Handler para atualizar configuração global"""
    
    def __init__(self, repository: ConfigurationRepository):
        self.repository = repository
    
    def handle(self, command: UpdateConfigurationCommand) -> Configuration:
        """Executa o use case de atualizar configuração"""
        
        config = self.repository.get_global_config()
        
        if command.notifications_enabled is not None:
            if command.notifications_enabled:
                config.enable_notifications()
            else:
                config.disable_notifications()
        
        if command.support_email is not None:
            config.update_support_email(command.support_email)
        
        if command.maintenance_mode is not None:
            if command.maintenance_mode:
                config.enable_maintenance_mode()
            else:
                config.disable_maintenance_mode()
        
        return self.repository.save(config)