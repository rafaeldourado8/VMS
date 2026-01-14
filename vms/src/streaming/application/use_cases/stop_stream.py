from domain.repositories.stream_repository import IStreamRepository
from domain.repositories.streaming_provider import IStreamingProvider

class StopStreamUseCase:
    def __init__(self, stream_repo: IStreamRepository, provider: IStreamingProvider):
        self._stream_repo = stream_repo
        self._provider = provider
    
    def execute(self, camera_id: str) -> None:
        stream = self._stream_repo.find_by_camera_id(camera_id)
        if not stream:
            raise ValueError(f"Stream not found for camera {camera_id}")
        
        # Para stream no MediaMTX
        self._provider.delete_stream(camera_id)
        
        # Atualiza status
        stream.stop()
        self._stream_repo.save(stream)
