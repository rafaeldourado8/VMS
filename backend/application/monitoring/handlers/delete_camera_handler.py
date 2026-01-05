from domain.monitoring.repositories.camera_repository import CameraRepository
from domain.monitoring.exceptions import CameraNotFoundException
from ..commands.delete_camera_command import DeleteCameraCommand


class DeleteCameraHandler:
    """Handler para deletar câmera"""
    
    def __init__(self, repository: CameraRepository):
        self.repository = repository
    
    def handle(self, command: DeleteCameraCommand) -> None:
        """Executa o use case de deletar câmera"""
        
        camera = self.repository.find_by_id(command.camera_id)
        
        if not camera:
            raise CameraNotFoundException(f"Câmera {command.camera_id} não encontrada")
        
        if camera.owner_id != command.owner_id:
            raise PermissionError("Usuário não tem permissão para deletar esta câmera")
        
        self.repository.delete(command.camera_id)
