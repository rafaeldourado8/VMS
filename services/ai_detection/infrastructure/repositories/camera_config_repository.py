from typing import Dict, Any


class InMemoryCameraConfigRepository:
    """Repositório em memória para configurações de câmera"""
    
    def __init__(self):
        self._configs: Dict[int, Dict[str, Any]] = {}
    
    def get_or_create(self, camera_id: int) -> Dict[str, Any]:
        """Obtém ou cria configuração padrão"""
        if camera_id not in self._configs:
            self._configs[camera_id] = {
                'ai_enabled': True,
                'roi': None,
                'virtual_lines': None
            }
        return self._configs[camera_id].copy()
    
    def save(self, camera_id: int, config: Dict[str, Any]) -> None:
        """Salva configuração"""
        self._configs[camera_id] = config
    
    def get(self, camera_id: int) -> Dict[str, Any]:
        """Obtém configuração"""
        return self._configs.get(camera_id, {})
    
    def is_ai_enabled(self, camera_id: int) -> bool:
        """Verifica se IA está habilitada"""
        config = self.get(camera_id)
        return config.get('ai_enabled', True)
