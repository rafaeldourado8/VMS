from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class MediaMTXAdapter(ABC):
    
    @abstractmethod
    def add_path(self, path_name: str, source_url: str) -> bool:
        """
        Adiciona path no MediaMTX via API.
        """
        pass
    
    @abstractmethod
    def remove_path(self, path_name: str) -> bool:
        """
        Remove path do MediaMTX via API.
        """
        pass
    
    @abstractmethod
    def path_exists(self, path_name: str) -> bool:
        """
        Verifica se path existe no MediaMTX.
        """
        pass
    
    @abstractmethod
    def get_hls_url(self, path_name: str) -> str:
        """
        Retorna URL HLS para o path.
        """
        pass
    
    @abstractmethod
    def update_path_config(self, path_name: str, config: Dict[str, Any]) -> bool:
        """
        Atualiza configuração de um path existente.
        """
        pass
    
    @abstractmethod
    def get_path(self, path_name: str) -> Optional[Dict[str, Any]]:
        """
        Retorna informações de um path.
        """
        pass
    
    @abstractmethod
    def get_all_paths(self) -> Optional[Dict[str, Any]]:
        """
        Retorna todos os paths ativos.
        """
        pass
