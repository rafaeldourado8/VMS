import redis.asyncio as redis
from typing import Optional, Any
import json
import logging
import pickle

from ..core.interfaces import ICacheService
from ..config import settings

logger = logging.getLogger(__name__)

class RedisCacheService(ICacheService):
    """Serviço de cache Redis (Single Responsibility)"""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    async def connect(self) -> bool:
        """Conecta ao Redis"""
        try:
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=False
            )
            
            await self._client.ping()
            logger.info("Conectado ao Redis")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao Redis: {str(e)}")
            return False
    
    async def disconnect(self) -> None:
        """Desconecta do Redis"""
        if self._client:
            await self._client.close()
            logger.info("Desconectado do Redis")
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        try:
            if not self._client:
                return None
            
            value = await self._client.get(key)
            
            if value is None:
                return None
            
            # Tenta deserializar
            try:
                return pickle.loads(value)
            except:
                return value.decode('utf-8')
                
        except Exception as e:
            logger.error(f"Erro ao obter do cache: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Define valor no cache"""
        try:
            if not self._client:
                return False
            
            # Serializa valor
            try:
                serialized = pickle.dumps(value)
            except:
                serialized = str(value).encode('utf-8')
            
            if ttl:
                await self._client.setex(key, ttl, serialized)
            else:
                await self._client.set(key, serialized)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir no cache: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        try:
            if not self._client:
                return False
            
            result = await self._client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Erro ao deletar do cache: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        try:
            if not self._client:
                return False
            
            result = await self._client.exists(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Erro ao verificar existência: {str(e)}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Incrementa valor"""
        try:
            if not self._client:
                return None
            
            return await self._client.incrby(key, amount)
            
        except Exception as e:
            logger.error(f"Erro ao incrementar: {str(e)}")
            return None
    
    async def get_many(self, keys: list) -> dict:
        """Obtém múltiplos valores"""
        try:
            if not self._client:
                return {}
            
            values = await self._client.mget(keys)
            
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        result[key] = pickle.loads(value)
                    except:
                        result[key] = value.decode('utf-8')
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter múltiplos valores: {str(e)}")
            return {}
    
    async def set_many(self, mapping: dict, ttl: Optional[int] = None) -> bool:
        """Define múltiplos valores"""
        try:
            if not self._client:
                return False
            
            pipe = self._client.pipeline()
            
            for key, value in mapping.items():
                try:
                    serialized = pickle.dumps(value)
                except:
                    serialized = str(value).encode('utf-8')
                
                if ttl:
                    pipe.setex(key, ttl, serialized)
                else:
                    pipe.set(key, serialized)
            
            await pipe.execute()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir múltiplos valores: {str(e)}")
            return False