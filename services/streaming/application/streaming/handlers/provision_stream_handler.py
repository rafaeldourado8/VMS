from domain.streaming.entities.stream import Stream
from domain.streaming.value_objects.stream_path import StreamPath
from domain.streaming.value_objects.hls_url import HLSUrl
from domain.streaming.repositories.stream_repository import StreamRepository
from domain.streaming.exceptions import StreamAlreadyExistsException
from ..commands.provision_stream_command import ProvisionStreamCommand


class ProvisionStreamHandler:
    """Handler para provisionar stream"""
    
    def __init__(self, repository: StreamRepository, base_url: str = "http://localhost:8889"):
        self.repository = repository
        self.base_url = base_url
    
    def handle(self, command: ProvisionStreamCommand) -> Stream:
        """Executa o use case de provisionar stream"""
        
        if self.repository.exists(command.camera_id):
            raise StreamAlreadyExistsException(f"Stream para câmera {command.camera_id} já existe")
        
        path = StreamPath(command.camera_id)
        hls_url = HLSUrl(self.base_url, str(path))
        
        stream = Stream(
            camera_id=command.camera_id,
            rtsp_url=command.rtsp_url,
            path=path,
            hls_url=hls_url,
            on_demand=command.on_demand
        )
        
        stream.start()
        
        return self.repository.save(stream)
