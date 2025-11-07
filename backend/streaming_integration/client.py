"""
Cliente HTTP para comunicação com o serviço de streaming FastAPI.
Singleton thread-safe para reutilização de conexões.
"""

import logging
from typing import Optional, Dict, Any, List
import httpx
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class StreamingServiceClient:
    """Cliente singleton para comunicação com o serviço de streaming."""
    
    _instance = None
    _lock = None
    
    def __new__(cls):
        if cls._instance is None:
            import threading
            cls._lock = threading.Lock()
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_url = getattr(
            settings, 
            'STREAMING_SERVICE_URL', 
            'http://streaming_service:8001'
        )
        self.api_prefix = '/api/v1'
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        self.api_key = getattr(settings, 'STREAMING_API_KEY', None)
        self._initialized = True
        
        logger.info(f"StreamingServiceClient inicializado: {self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisições."""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        return headers
    
    def _handle_error(self, operation: str, error: Exception, **context):
        """Centraliza tratamento de erros."""
        logger.error(
            f"Erro em {operation}: {error}",
            extra=context,
            exc_info=True
        )
    
    async def create_stream(
        self, 
        camera_id: int, 
        stream_url: str,
        protocol: str = "rtsp"
    ) -> Optional[Dict[str, Any]]:
        """Cria um novo stream."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}{self.api_prefix}/streams/",
                    json={
                        "camera_id": camera_id,
                        "stream_url": stream_url,
                        "protocol": protocol
                    },
                    headers=self._get_headers()
                )
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Stream criado: {data.get('stream_id')} para câmera {camera_id}")
                
                # Cache do stream_id
                cache.set(f"stream_camera_{camera_id}", data.get('stream_id'), 3600)
                
                return data
                
        except Exception as e:
            self._handle_error("create_stream", e, camera_id=camera_id)
            return None
    
    async def get_stream(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Obtém informações de um stream."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}{self.api_prefix}/streams/{stream_id}",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            self._handle_error("get_stream", e, stream_id=stream_id)
            return None
    
    async def list_streams(self) -> List[Dict[str, Any]]:
        """Lista todos os streams ativos."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}{self.api_prefix}/streams/",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            self._handle_error("list_streams", e)
            return []
    
    async def delete_stream(self, stream_id: str) -> bool:
        """Deleta um stream."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    f"{self.base_url}{self.api_prefix}/streams/{stream_id}",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                logger.info(f"Stream {stream_id} deletado")
                return True
                
        except Exception as e:
            self._handle_error("delete_stream", e, stream_id=stream_id)
            return False
    
    async def update_stream(
        self, 
        stream_id: str,
        stream_url: Optional[str] = None,
        protocol: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Atualiza um stream."""
        try:
            data = {}
            if stream_url:
                data['stream_url'] = stream_url
            if protocol:
                data['protocol'] = protocol
                
            if not data:
                return None
                
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.patch(
                    f"{self.base_url}{self.api_prefix}/streams/{stream_id}",
                    json=data,
                    headers=self._get_headers()
                )
                response.raise_for_status()
                logger.info(f"Stream {stream_id} atualizado")
                return response.json()
                
        except Exception as e:
            self._handle_error("update_stream", e, stream_id=stream_id)
            return None
    
    async def health_check(self) -> bool:
        """Verifica saúde do serviço."""
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return True
                
        except Exception:
            return False


# Instância singleton
streaming_client = StreamingServiceClient()