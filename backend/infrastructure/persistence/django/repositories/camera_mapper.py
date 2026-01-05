from typing import Optional
from domain.monitoring.entities.camera import Camera, CameraStatus
from domain.monitoring.value_objects.stream_url import StreamUrl
from domain.monitoring.value_objects.location import Location
from domain.monitoring.value_objects.geo_coordinates import GeoCoordinates
from ..models.camera_model import CameraModel


class CameraMapper:
    """Mapper entre entidade Camera e CameraModel Django"""
    
    @staticmethod
    def to_domain(model: CameraModel) -> Camera:
        """Converte CameraModel para entidade Camera"""
        return Camera(
            id=model.id,
            owner_id=model.owner_id,
            name=model.name,
            stream_url=StreamUrl(model.stream_url),
            status=CameraStatus(model.status),
            location=Location(model.location),
            coordinates=GeoCoordinates(model.latitude, model.longitude),
            thumbnail_url=model.thumbnail_url,
            recording_enabled=model.recording_enabled,
            recording_retention_days=model.recording_retention_days,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    @staticmethod
    def to_model(camera: Camera, model: Optional[CameraModel] = None) -> CameraModel:
        """Converte entidade Camera para CameraModel"""
        if model is None:
            model = CameraModel()
        
        model.owner_id = camera.owner_id
        model.name = camera.name
        model.stream_url = str(camera.stream_url)
        model.status = camera.status.value
        model.location = camera.location.name
        model.latitude = camera.coordinates.latitude
        model.longitude = camera.coordinates.longitude
        model.thumbnail_url = camera.thumbnail_url
        model.recording_enabled = camera.recording_enabled
        model.recording_retention_days = camera.recording_retention_days
        
        return model
