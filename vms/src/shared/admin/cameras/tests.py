from django.test import TestCase
from shared.admin.cidades.models import City
from shared.admin.cameras.models import Camera
from shared.admin.cameras.enums import CameraProtocol

class CameraModelTest(TestCase):
    
    def setUp(self):
        self.city = City.objects.create(name="São Paulo")
    
    def test_create_camera(self):
        camera = Camera.objects.create(
            city=self.city,
            name="Câmera 01",
            stream_url="rtsp://192.168.1.100:554/stream",
            protocol=CameraProtocol.RTSP
        )
        self.assertIsNotNone(camera.id)
        self.assertIsNotNone(camera.public_id)
        self.assertNotEqual(camera.id, camera.public_id)
    
    def test_camera_uuid_primary_key(self):
        camera = Camera.objects.create(
            city=self.city,
            name="Câmera 02",
            stream_url="rtsp://test",
            protocol=CameraProtocol.RTSP
        )
        self.assertEqual(len(str(camera.id)), 36)
        self.assertEqual(len(str(camera.public_id)), 36)
    
    def test_camera_belongs_to_city(self):
        camera = Camera.objects.create(
            city=self.city,
            name="Câmera 03",
            stream_url="rtsp://test",
            protocol=CameraProtocol.RTSP
        )
        self.assertEqual(camera.city, self.city)
        self.assertIn(camera, self.city.cameras.all())
    
    def test_camera_default_values(self):
        camera = Camera.objects.create(
            city=self.city,
            name="Câmera 04",
            stream_url="rtsp://test",
            protocol=CameraProtocol.RTSP
        )
        self.assertFalse(camera.is_lpr)
        self.assertTrue(camera.is_active)
    
    def test_camera_unique_name_per_city(self):
        Camera.objects.create(
            city=self.city,
            name="Câmera Duplicada",
            stream_url="rtsp://test1",
            protocol=CameraProtocol.RTSP
        )
        with self.assertRaises(Exception):
            Camera.objects.create(
                city=self.city,
                name="Câmera Duplicada",
                stream_url="rtsp://test2",
                protocol=CameraProtocol.RTSP
            )
    
    def test_camera_same_name_different_cities(self):
        city2 = City.objects.create(name="Rio de Janeiro")
        
        camera1 = Camera.objects.create(
            city=self.city,
            name="Câmera Principal",
            stream_url="rtsp://test1",
            protocol=CameraProtocol.RTSP
        )
        camera2 = Camera.objects.create(
            city=city2,
            name="Câmera Principal",
            stream_url="rtsp://test2",
            protocol=CameraProtocol.RTSP
        )
        self.assertNotEqual(camera1.id, camera2.id)
    
    def test_camera_cascade_delete_with_city(self):
        camera = Camera.objects.create(
            city=self.city,
            name="Câmera Temp",
            stream_url="rtsp://test",
            protocol=CameraProtocol.RTSP
        )
        camera_id = camera.id
        self.city.delete()
        self.assertFalse(Camera.objects.filter(id=camera_id).exists())
    
    def test_camera_str_representation(self):
        camera = Camera.objects.create(
            city=self.city,
            name="Câmera 05",
            stream_url="rtsp://test",
            protocol=CameraProtocol.RTSP
        )
        self.assertEqual(str(camera), "Câmera 05 (São Paulo)")
    
    def test_public_id_is_unique(self):
        camera1 = Camera.objects.create(
            city=self.city,
            name="Câmera A",
            stream_url="rtsp://test1",
            protocol=CameraProtocol.RTSP
        )
        camera2 = Camera.objects.create(
            city=self.city,
            name="Câmera B",
            stream_url="rtsp://test2",
            protocol=CameraProtocol.RTSP
        )
        self.assertNotEqual(camera1.public_id, camera2.public_id)
