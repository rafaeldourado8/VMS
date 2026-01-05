from typing import Optional, List, Dict
from domain.streaming.entities.stream import Stream
from domain.streaming.repositories.stream_repository import StreamRepository


class InMemoryStreamRepository(StreamRepository):
    """Implementação em memória do repositório de streams"""
    
    def __init__(self):
        self._streams: Dict[int, Stream] = {}
    
    def save(self, stream: Stream) -> Stream:
        """Salva ou atualiza um stream"""
        self._streams[stream.camera_id] = stream
        return stream
    
    def find_by_camera(self, camera_id: int) -> Optional[Stream]:
        """Busca stream por camera_id"""
        return self._streams.get(camera_id)
    
    def find_all(self) -> List[Stream]:
        """Lista todos os streams"""
        return list(self._streams.values())
    
    def delete(self, camera_id: int) -> None:
        """Remove um stream"""
        if camera_id in self._streams:
            del self._streams[camera_id]
    
    def exists(self, camera_id: int) -> bool:
        """Verifica se stream existe"""
        return camera_id in self._streams
