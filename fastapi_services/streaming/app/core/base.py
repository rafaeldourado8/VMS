from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseStreamReader(ABC):
    """Classe base para leitores de stream (Open/Closed Principle)"""
    
    def __init__(self, stream_url: str):
        self.stream_url = stream_url
        self._connected = False
        self._properties: Dict[str, Any] = {}
        self._error_count = 0
        self._max_errors = 10
    
    async def connect(self) -> bool:
        """Template method para conexão"""
        try:
            logger.info(f"Conectando ao stream: {self.stream_url}")
            
            # Hook para validação pré-conexão
            if not await self._pre_connect():
                return False
            
            # Conexão específica da implementação
            success = await self._do_connect()
            
            if success:
                self._connected = True
                self._error_count = 0
                
                # Hook pós-conexão
                await self._post_connect()
                
                logger.info(f"Conectado com sucesso: {self.stream_url}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao conectar: {str(e)}")
            return False
    
    async def read_frame(self) -> Optional[Any]:
        """Template method para leitura de frame"""
        if not self._connected:
            return None
        
        try:
            frame = await self._do_read_frame()
            
            if frame is None:
                self._error_count += 1
                
                if self._error_count >= self._max_errors:
                    logger.error(f"Máximo de erros atingido: {self._error_count}")
                    await self.disconnect()
                    return None
            else:
                self._error_count = 0
            
            return frame
            
        except Exception as e:
            logger.error(f"Erro ao ler frame: {str(e)}")
            self._error_count += 1
            return None
    
    async def disconnect(self) -> None:
        """Template method para desconexão"""
        if not self._connected:
            return
        
        try:
            await self._do_disconnect()
            self._connected = False
            logger.info(f"Desconectado: {self.stream_url}")
            
        except Exception as e:
            logger.error(f"Erro ao desconectar: {str(e)}")
    
    def is_connected(self) -> bool:
        return self._connected
    
    def get_properties(self) -> Dict[str, Any]:
        return self._properties.copy()
    
    # Hooks para subclasses (Template Method Pattern)
    async def _pre_connect(self) -> bool:
        """Hook executado antes da conexão"""
        return True
    
    async def _post_connect(self) -> None:
        """Hook executado após conexão bem-sucedida"""
        pass
    
    # Métodos abstratos que devem ser implementados
    @abstractmethod
    async def _do_connect(self) -> bool:
        """Implementação específica da conexão"""
        pass
    
    @abstractmethod
    async def _do_read_frame(self) -> Optional[Any]:
        """Implementação específica da leitura"""
        pass
    
    @abstractmethod
    async def _do_disconnect(self) -> None:
        """Implementação específica da desconexão"""
        pass


class BaseFrameProcessor(ABC):
    """Classe base para processadores de frame"""
    
    def __init__(self):
        self._enabled = True
        self._stats = {
            "processed": 0,
            "errors": 0,
            "total_time": 0.0
        }
    
    async def process(self, frame: Any) -> Any:
        """Template method para processamento"""
        if not self._enabled:
            return frame
        
        start_time = datetime.now()
        
        try:
            # Validação
            if not await self._validate_frame(frame):
                return frame
            
            # Processamento
            processed_frame = await self._do_process(frame)
            
            # Atualiza estatísticas
            self._stats["processed"] += 1
            elapsed = (datetime.now() - start_time).total_seconds()
            self._stats["total_time"] += elapsed
            
            return processed_frame
            
        except Exception as e:
            logger.error(f"Erro no processamento: {str(e)}")
            self._stats["errors"] += 1
            return frame
    
    def enable(self):
        self._enabled = True
    
    def disable(self):
        self._enabled = False
    
    def get_stats(self) -> Dict[str, Any]:
        return self._stats.copy()
    
    async def _validate_frame(self, frame: Any) -> bool:
        """Hook para validação"""
        return frame is not None
    
    @abstractmethod
    async def _do_process(self, frame: Any) -> Any:
        """Implementação específica do processamento"""
        pass