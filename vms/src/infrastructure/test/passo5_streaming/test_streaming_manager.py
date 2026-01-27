from django.test import TestCase
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from shared.admin.cidades.models import City
from shared.admin.cameras.models import Camera
from shared.admin.cameras.enums import CameraProtocol
from infrastructure.cache.streaming import RedisStreamingManager
from infrastructure.servers.mediamtx import MediaMTXAdapter

class MockMediaMTXAdapter(MediaMTXAdapter):
    def __init__(self):
        self.paths = {}
    
    def add_path(self, path_name: str, source_url: str) -> bool:
        self.paths[path_name] = source_url
        return True
    
    def remove_path(self, path_name: str) -> bool:
        if path_name in self.paths:
            del self.paths[path_name]
            return True
        return False
    
    def path_exists(self, path_name: str) -> bool:
        return path_name in self.paths
    
    def get_hls_url(self, path_name: str) -> str:
        return f"/hls/{path_name}/index.m3u8"

class StreamingManagerTest(TestCase):
    
    def setUp(self):
        self.city = City.objects.create(name="São Paulo")
        self.camera = Camera.objects.create(
            city=self.city,
            name="Câmera 01",
            stream_url="rtsp://test:554/stream",
            protocol=CameraProtocol.RTSP,
            is_active=True
        )
        
        self.redis_mock = MagicMock()
        self.mediamtx = MockMediaMTXAdapter()
        self.manager = RedisStreamingManager(self.redis_mock, self.mediamtx)
    
    def test_start_stream_success(self):
        session = self.manager.start_stream(self.camera.id, self.city.id, 1)
        
        self.assertIsNotNone(session)
        self.assertEqual(session.camera_id, self.camera.id)
        self.assertEqual(session.city_id, self.city.id)
        self.assertTrue(session.session_id.startswith("stream_"))
        self.redis_mock.setex.assert_called_once()
        self.redis_mock.sadd.assert_called_once()
    
    def test_start_stream_camera_not_found(self):
        with self.assertRaises(ValueError) as ctx:
            self.manager.start_stream(uuid4(), self.city.id, 1)
        self.assertEqual(str(ctx.exception), "Camera not found")
    
    def test_start_stream_camera_inactive(self):
        self.camera.is_active = False
        self.camera.save()
        
        with self.assertRaises(ValueError) as ctx:
            self.manager.start_stream(self.camera.id, self.city.id, 1)
        self.assertEqual(str(ctx.exception), "Camera is not active")
    
    def test_start_stream_wrong_city(self):
        other_city = City.objects.create(name="Rio de Janeiro")
        
        with self.assertRaises(ValueError):
            self.manager.start_stream(self.camera.id, other_city.id, 1)
    
    def test_mediamtx_path_added(self):
        session = self.manager.start_stream(self.camera.id, self.city.id, 1)
        
        self.assertTrue(self.mediamtx.path_exists(session.session_id))
        self.assertEqual(
            self.mediamtx.paths[session.session_id],
            self.camera.stream_url
        )
