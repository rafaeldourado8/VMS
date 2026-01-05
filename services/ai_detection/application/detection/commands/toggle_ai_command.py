from dataclasses import dataclass


@dataclass
class ToggleAICommand:
    """Command para ativar/desativar IA em uma câmera"""
    
    camera_id: int
    enabled: bool
