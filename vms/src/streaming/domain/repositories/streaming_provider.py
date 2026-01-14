from abc import ABC, abstractmethod

class IStreamingProvider(ABC):
    """Interface para provedor de streaming (MediaMTX)"""
    
    @abstractmethod
    def create_stream(self, camera_id: str, stream_url: str) -> str:
        """
        Cria stream HLS no MediaMTX
        Returns: HLS URL (http://mediamtx:8888/camera_{id}/index.m3u8)
        """
        pass
    
    @abstractmethod
    def delete_stream(self, camera_id: str) -> None:
        """Remove stream do MediaMTX"""
        pass
    
    @abstractmethod
    def is_stream_active(self, camera_id: str) -> bool:
        """Verifica se stream está ativo"""
        pass
