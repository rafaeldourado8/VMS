from ..commands.toggle_ai_command import ToggleAICommand


class ToggleAIHandler:
    """Handler para ativar/desativar IA"""
    
    def __init__(self, config_repository):
        self.config_repository = config_repository
    
    def handle(self, command: ToggleAICommand) -> dict:
        """Ativa ou desativa IA para uma câmera"""
        
        config = self.config_repository.get_or_create(command.camera_id)
        config['ai_enabled'] = command.enabled
        self.config_repository.save(command.camera_id, config)
        
        return {
            'camera_id': command.camera_id,
            'ai_enabled': command.enabled,
            'message': f"IA {'ativada' if command.enabled else 'desativada'}"
        }
