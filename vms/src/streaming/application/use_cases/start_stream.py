from uuid import uuid4
from domain.entities.stream import Stream
from domain.repositories.stream_repository import IStreamRepository
from domain.repositories.streaming_provider import IStreamingProvider

class StartStreamUseCase:
    def __init__(self, stream_repo: IStreamRepository, provider: IStreamingProvider):
        self._stream_repo = stream_repo
        self._provider = provider
    
    def execute(self, camera_id: str, stream_url: str) -> str:
        # Verifica se já existe stream ativo
        existing = self._stream_repo.find_by_camera_id(camera_id)
        if existing and existing.is_active():
            return existing.hls_url
        
        # Cria stream no MediaMTX
        hls_url = self._provider.create_stream(camera_id, stream_url)
        
        # Salva no repositório
        stream = Stream(
            id=str(uuid4()),
            camera_id=camera_id,
            hls_url=hls_url
        )
        stream.start()
        
        self._stream_repo.save(stream)
        return hls_url
