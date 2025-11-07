from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import numpy as np

class IStreamReader(ABC):
    """Interface para leitores de stream"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Conecta ao stream"""
        pass
    
    @abstractmethod
    async def read_frame(self) -> Optional[np.ndarray]:
        """Lê um frame do stream"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Desconecta do stream"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Verifica se está conectado"""
        pass
    
    @abstractmethod
    def get_properties(self) -> Dict[str, Any]:
        """Retorna propriedades do stream"""
        pass


class IFrameProcessor(ABC):
    """Interface para processadores de frame"""
    
    @abstractmethod
    async def process(self, frame: np.ndarray) -> np.ndarray:
        """Processa um frame"""
        pass


class IFrameEncoder(ABC):
    """Interface para encoders de frame"""
    
    @abstractmethod
    async def encode(self, frame: np.ndarray) -> bytes:
        """Codifica um frame"""
        pass


class IStreamRepository(ABC):
    """Interface para repositório de streams"""
    
    @abstractmethod
    async def save_session(self, session_data: Dict[str, Any]) -> int:
        """Salva sessão de stream"""
        pass
    
    @abstractmethod
    async def update_session(self, session_id: int, data: Dict[str, Any]) -> bool:
        """Atualiza sessão"""
        pass
    
    @abstractmethod
    async def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Obtém sessão"""
        pass
    
    @abstractmethod
    async def save_metrics(self, metrics_data: Dict[str, Any]) -> int:
        """Salva métricas"""
        pass


class ICacheService(ABC):
    """Interface para serviço de cache"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Define valor no cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        pass