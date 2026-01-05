from domain.monitoring.entities.camera import Camera
from domain.monitoring.value_objects.stream_url import StreamUrl
from domain.monitoring.value_objects.location import Location
from domain.monitoring.value_objects.geo_coordinates import GeoCoordinates
from domain.monitoring.repositories.camera_repository import CameraRepository
from ..commands.create_camera_command import CreateCameraCommand


class CreateCameraHandler:
    """Handler para criar câmera"""
    
    def __init__(self, repository: CameraRepository):
        self.repository = repository
    
    def handle(self, command: CreateCameraCommand) -> Camera:
        """Executa o use case de criar câmera"""
        
        if self.repository.exists_by_name(command.name):
            raise ValueError(f"Câmera com nome '{command.name}' já existe")
        
        camera = Camera(
            id=None,
            owner_id=command.owner_id,
            name=command.name,
            stream_url=StreamUrl(command.stream_url),
            location=Location(command.location),
            coordinates=GeoCoordinates(command.latitude, command.longitude),
            thumbnail_url=command.thumbnail_url
        )
        
        return self.repository.save(camera)
