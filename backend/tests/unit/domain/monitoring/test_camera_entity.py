import pytest
from domain.monitoring.entities.camera import Camera, CameraStatus
from domain.monitoring.value_objects.stream_url import StreamUrl
from domain.monitoring.value_objects.location import Location
from domain.monitoring.value_objects.geo_coordinates import GeoCoordinates


def test_create_camera():
    camera = Camera(
        id=1,
        owner_id=100,
        name="Câmera Principal",
        stream_url=StreamUrl("rtsp://192.168.1.100:554/stream")
    )
    assert camera.id == 1
    assert camera.name == "Câmera Principal"
    assert camera.is_online()


def test_activate_camera():
    camera = Camera(
        id=1,
        owner_id=100,
        name="Test",
        stream_url=StreamUrl("rtsp://test.com"),
        status=CameraStatus.OFFLINE
    )
    camera.activate()
    assert camera.is_online()


def test_deactivate_camera():
    camera = Camera(
        id=1,
        owner_id=100,
        name="Test",
        stream_url=StreamUrl("rtsp://test.com")
    )
    camera.deactivate()
    assert not camera.is_online()


def test_update_location():
    camera = Camera(
        id=1,
        owner_id=100,
        name="Test",
        stream_url=StreamUrl("rtsp://test.com")
    )
    location = Location("Centro")
    coords = GeoCoordinates(-23.5505, -46.6333)
    
    camera.update_location(location, coords)
    
    assert camera.location == location
    assert camera.coordinates == coords


def test_enable_recording():
    camera = Camera(
        id=1,
        owner_id=100,
        name="Test",
        stream_url=StreamUrl("rtsp://test.com"),
        recording_enabled=False
    )
    camera.enable_recording(retention_days=15)
    
    assert camera.recording_enabled
    assert camera.recording_retention_days == 15


def test_enable_recording_invalid_retention_defaults_to_30():
    camera = Camera(
        id=1,
        owner_id=100,
        name="Test",
        stream_url=StreamUrl("rtsp://test.com")
    )
    camera.enable_recording(retention_days=99)
    
    assert camera.recording_retention_days == 30


def test_disable_recording():
    camera = Camera(
        id=1,
        owner_id=100,
        name="Test",
        stream_url=StreamUrl("rtsp://test.com")
    )
    camera.disable_recording()
    
    assert not camera.recording_enabled
