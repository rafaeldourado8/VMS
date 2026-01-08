from typing import Any, Optional
import hashlib

from django.core.cache import cache

class CacheService:
    """Serviço centralizado de cache"""
    
    # TTL padrões (em segundos)
    DEFAULT_TTL = 300  # 5 minutos
    ANALYTICS_TTL = 60  # 1 minuto
    CAMERA_STATUS_TTL = 30  # 30 segundos
    
    @staticmethod
    def _make_key(prefix: str, *args) -> str:
        """Cria chave de cache consistente"""
        key_data = f"{prefix}:{':'.join(map(str, args))}"
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    @classmethod
    def get_analytics(cls, user_id: int, period: str) -> Optional[dict]:
        """Cache para dados de analytics"""
        key = cls._make_key("analytics", user_id, period)
        return cache.get(key)
    
    @classmethod
    def set_analytics(cls, user_id: int, period: str, data: dict) -> None:
        """Armazena dados de analytics no cache"""
        key = cls._make_key("analytics", user_id, period)
        cache.set(key, data, cls.ANALYTICS_TTL)
    
    @classmethod
    def invalidate_user_data(cls, user_id: int) -> None:
        """Invalida caches do usuário"""
        key = cls._make_key("analytics", user_id, "*")
        cache.delete(key)