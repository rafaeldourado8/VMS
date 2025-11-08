from typing import Optional
from fastapi import Depends
import logging

from ..services.stream_manager import StreamManager
from ..services.cache_service import RedisCacheService
from ..repositories.stream_repository import StreamRepository

logger = logging.getLogger(__name__)

# Singletons
_stream_manager: Optional[StreamManager] = None
_cache_service: Optional[RedisCacheService] = None

async def get_stream_service() -> StreamManager:
    """Dependency Injection para StreamManager"""
    global _stream_manager
    
    if _stream_manager is None:
        _stream_manager = StreamManager()
        logger.info("StreamManager inicializado")
    
    return _stream_manager

async def get_cache_service() -> RedisCacheService:
    """Dependency Injection para CacheService"""
    global _cache_service
    
    if _cache_service is None:
        _cache_service = RedisCacheService()
        await _cache_service.connect()
        logger.info("CacheService inicializado")
    
    return _cache_service

async def get_redis_client():
    """Dependency Injection para Redis Client"""
    cache_service = await get_cache_service()
    return cache_service

async def get_stream_repository(db = Depends(get_db_session)) -> StreamRepository:
    """Dependency Injection para StreamRepository"""
    return StreamRepository(db)

# Database session (exemplo - ajustar conforme seu setup)
async def get_db_session():
    """Dependency Injection para Database Session"""
    # Implementar conforme sua configuração de banco
    pass