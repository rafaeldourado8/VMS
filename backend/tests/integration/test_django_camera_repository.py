import pytest
from django.contrib.auth import get_user_model
from infrastructure.persistence.django.repositories.django_camera_repository import DjangoCameraRepository
from domain.monitoring.entities.camera import Camera
from domain.monitoring.value_objects.stream_url import StreamUrl
from domain.monitoring.value_objects.location import Location
from domain.monitoring.value_objects.geo_coordinates import GeoCoordinates

User = get_user_model()


@pytest.mark.django_db
class TestDjangoCameraRepository:
    
    def test_save_new_camera(self):
        user = User.objects.create_user(email="test@test.com", name="Test User", password="test123")
        repo = DjangoCameraRepository()
        
        camera = Camera(
            id=None,
            owner_id=user.id,
            name="Test Camera",
            stream_url=StreamUrl("rtsp://test.com")
        )
        
        saved = repo.save(camera)
        
        assert saved.id is not None
        assert saved.name == "Test Camera"
    
    def test_find_by_id(self):
        user = User.objects.create_user(email="test@test.com", name="Test User", password="test123")
        repo = DjangoCameraRepository()
        
        camera = Camera(
            id=None,
            owner_id=user.id,
            name="Find Test",
            stream_url=StreamUrl("rtsp://find.com")
        )
        saved = repo.save(camera)
        
        found = repo.find_by_id(saved.id)
        
        assert found is not None
        assert found.name == "Find Test"
    
    def test_find_by_owner(self):
        user = User.objects.create_user(email="test@test.com", name="Test User", password="test123")
        repo = DjangoCameraRepository()
        
        camera1 = Camera(
            id=None,
            owner_id=user.id,
            name="Camera 1",
            stream_url=StreamUrl("rtsp://cam1.com")
        )
        camera2 = Camera(
            id=None,
            owner_id=user.id,
            name="Camera 2",
            stream_url=StreamUrl("rtsp://cam2.com")
        )
        
        repo.save(camera1)
        repo.save(camera2)
        
        cameras = repo.find_by_owner(user.id)
        
        assert len(cameras) == 2
    
    def test_delete_camera(self):
        user = User.objects.create_user(email="test@test.com", name="Test User", password="test123")
        repo = DjangoCameraRepository()
        
        camera = Camera(
            id=None,
            owner_id=user.id,
            name="Delete Test",
            stream_url=StreamUrl("rtsp://delete.com")
        )
        saved = repo.save(camera)
        
        repo.delete(saved.id)
        
        found = repo.find_by_id(saved.id)
        assert found is None
    
    def test_exists_by_name(self):
        user = User.objects.create_user(email="test@test.com", name="Test User", password="test123")
        repo = DjangoCameraRepository()
        
        camera = Camera(
            id=None,
            owner_id=user.id,
            name="Unique Name",
            stream_url=StreamUrl("rtsp://unique.com")
        )
        repo.save(camera)
        
        assert repo.exists_by_name("Unique Name")
        assert not repo.exists_by_name("Non Existent")
