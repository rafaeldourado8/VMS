from domain.streaming.repositories.stream_repository import StreamRepository
from domain.streaming.exceptions import StreamNotFoundException
from ..commands.remove_stream_command import RemoveStreamCommand


class RemoveStreamHandler:
    """Handler para remover stream"""
    
    def __init__(self, repository: StreamRepository):
        self.repository = repository
    
    def handle(self, command: RemoveStreamCommand) -> None:
        """Executa o use case de remover stream"""
        
        stream = self.repository.find_by_camera(command.camera_id)
        
        if not stream:
            raise StreamNotFoundException(f"Stream para câmera {command.camera_id} não encontrado")
        
        stream.stop()
        self.repository.delete(command.camera_id)
