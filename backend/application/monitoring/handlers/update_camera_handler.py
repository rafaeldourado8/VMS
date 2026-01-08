from domain.monitoring.entities.camera import Camera
from domain.monitoring.repositories.camera_repository import CameraRepository
from domain.monitoring.value_objects.geo_coordinates import GeoCoordinates
from domain.monitoring.value_objects.location import Location
from domain.monitoring.value_objects.stream_url import StreamUrl

class UpdateCameraCommand:
    def __init__(self, camera_id: int, owner_id: int, **kwargs):
        self.camera_id = camera_id
        self.owner_id = owner_id
        self.name = kwargs.get('name')
        self.stream_url = kwargs.get('stream_url')
        self.location = kwargs.get('location')
        self.latitude = kwargs.get('latitude')
        self.longitude = kwargs.get('longitude')
        self.thumbnail_url = kwargs.get('thumbnail_url')

class UpdateCameraHandler:
    def __init__(self, repository: CameraRepository):
        self.repository = repository
    
    def handle(self, command: UpdateCameraCommand) -> Camera:
        camera = self.repository.find_by_id(command.camera_id)
        if not camera or camera.owner_id != command.owner_id:
            raise ValueError("Câmera não encontrada")
        
        if command.name:
            camera.name = command.name
        if command.stream_url:
            camera.stream_url = StreamUrl(command.stream_url)
        if command.location:
            camera.location = Location(command.location)
        if command.latitude is not None and command.longitude is not None:
            camera.coordinates = GeoCoordinates(command.latitude, command.longitude)
        if command.thumbnail_url:
            camera.thumbnail_url = command.thumbnail_url
        
        return self.repository.save(camera)
