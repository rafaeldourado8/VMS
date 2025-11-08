"""
Serviços de integração com streaming.
Camada de abstração entre o cliente HTTP e as views/signals.
"""

import logging
from typing import Optional, Dict, Any, List
from asgiref.sync import async_to_sync
from django.core.cache import cache
from .client import streaming_client

logger = logging.getLogger(__name__)


class StreamingService:
    """Serviço para gerenciar streams."""
    
    @staticmethod
    def create_stream_for_camera(camera) -> Optional[str]:
        """
        Cria um stream para uma câmera.
        
        Args:
            camera: Instância do modelo Camera
            
        Returns:
            stream_id ou None
        """
        # Verificar se já existe stream em cache
        cached_stream_id = cache.get(f"stream_camera_{camera.id}")
        if cached_stream_id:
            logger.info(f"Stream já existe em cache para câmera {camera.id}")
            return cached_stream_id
        
        # Obter URL e protocolo da câmera
        stream_url = getattr(camera, 'stream_url', None) or getattr(camera, 'rtsp_url', None)
        protocol = getattr(camera, 'protocol', 'rtsp')
        
        if not stream_url:
            logger.warning(f"Câmera {camera.id} não possui URL de stream")
            return None
        
        # Criar stream
        result = async_to_sync(streaming_client.create_stream)(
            camera_id=camera.id,
            stream_url=stream_url,
            protocol=protocol
        )
        
        if result:
            stream_id = result.get('stream_id')
            
            # Atualizar câmera se tiver campo stream_id
            if hasattr(camera, 'stream_id'):
                camera.stream_id = stream_id
                camera.save(update_fields=['stream_id'])
            
            return stream_id
        
        return None
    
    @staticmethod
    def delete_stream_for_camera(camera) -> bool:
        """
        Deleta o stream de uma câmera.
        
        Args:
            camera: Instância do modelo Camera
            
        Returns:
            True se deletado com sucesso
        """
        stream_id = getattr(camera, 'stream_id', None)
        
        if not stream_id:
            # Tentar obter do cache
            stream_id = cache.get(f"stream_camera_{camera.id}")
        
        if not stream_id:
            logger.warning(f"Câmera {camera.id} não possui stream_id")
            return False
        
        success = async_to_sync(streaming_client.delete_stream)(stream_id)
        
        if success:
            # Limpar cache
            cache.delete(f"stream_camera_{camera.id}")
            
            # Limpar stream_id da câmera
            if hasattr(camera, 'stream_id'):
                camera.stream_id = None
                camera.save(update_fields=['stream_id'])
        
        return success
    
    @staticmethod
    def update_stream_for_camera(camera) -> bool:
        """
        Atualiza o stream de uma câmera.
        
        Args:
            camera: Instância do modelo Camera
            
        Returns:
            True se atualizado com sucesso
        """
        stream_id = getattr(camera, 'stream_id', None)
        
        if not stream_id:
            logger.warning(f"Câmera {camera.id} não possui stream_id")
            return False
        
        stream_url = getattr(camera, 'stream_url', None) or getattr(camera, 'rtsp_url', None)
        protocol = getattr(camera, 'protocol', 'rtsp')
        
        result = async_to_sync(streaming_client.update_stream)(
            stream_id=stream_id,
            stream_url=stream_url,
            protocol=protocol
        )
        
        return result is not None
    
    @staticmethod
    def get_stream_status(camera) -> Optional[Dict[str, Any]]:
        """
        Obtém o status do stream de uma câmera.
        
        Args:
            camera: Instância do modelo Camera
            
        Returns:
            Dados do stream ou None
        """
        stream_id = getattr(camera, 'stream_id', None)
        
        if not stream_id:
            return None
        
        return async_to_sync(streaming_client.get_stream)(stream_id)
    
    @staticmethod
    def get_stream_url_for_frontend(camera) -> Optional[str]:
        """
        Retorna a URL do stream para o frontend.
        
        Args:
            camera: Instância do modelo Camera
            
        Returns:
            URL do stream ou None
        """
        stream_id = getattr(camera, 'stream_id', None)
        
        if not stream_id:
            return None
        
        return f"/streaming/api/v1/streams/{stream_id}/stream"
    
    @staticmethod
    def get_websocket_url(camera) -> Optional[str]:
        """
        Retorna a URL do WebSocket para o frontend.
        
        Args:
            camera: Instância do modelo Camera
            
        Returns:
            URL do WebSocket ou None
        """
        stream_id = getattr(camera, 'stream_id', None)
        
        if not stream_id:
            return None
        
        # Ajustar conforme seu domínio
        return f"ws://localhost/streaming/api/v1/streams/{stream_id}/ws"
    
    @staticmethod
    def health_check() -> bool:
        """Verifica se o serviço de streaming está saudável."""
        return async_to_sync(streaming_client.health_check)()