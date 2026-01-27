from django.test import TestCase
from uuid import uuid4
from shared.admin.cidades.models import City
from shared.admin.cameras.models import Camera
from shared.admin.cameras.enums import CameraProtocol
from infrastructure.repositories import DjangoCityRepository, DjangoCameraRepository

class CityRepositoryTest(TestCase):
    
    def setUp(self):
        self.repo = DjangoCityRepository()
        self.city = City.objects.create(name="São Paulo")
    
    def test_get_by_id(self):
        city = self.repo.get_by_id(self.city.id)
        self.assertEqual(city.id, self.city.id)
    
    def test_get_by_id_not_found(self):
        city = self.repo.get_by_id(uuid4())
        self.assertIsNone(city)
    
    def test_get_by_name(self):
        city = self.repo.get_by_name("São Paulo")
        self.assertEqual(city.id, self.city.id)
    
    def test_exists(self):
        self.assertTrue(self.repo.exists(self.city.id))
        self.assertFalse(self.repo.exists(uuid4()))
    
    def test_list_active(self):
        cities = self.repo.list_active()
        self.assertIn(self.city, cities)

class CameraRepositoryTest(TestCase):
    
    def setUp(self):
        self.repo = DjangoCameraRepository()
        self.city1 = City.objects.create(name="São Paulo")
        self.city2 = City.objects.create(name="Rio de Janeiro")
        self.camera = Camera.objects.create(
            city=self.city1,
            name="Câmera 01",
            stream_url="rtsp://test",
            protocol=CameraProtocol.RTSP
        )
    
    def test_get_by_id_with_correct_city(self):
        camera = self.repo.get_by_id(self.camera.id, self.city1.id)
        self.assertEqual(camera.id, self.camera.id)
    
    def test_get_by_id_with_wrong_city(self):
        camera = self.repo.get_by_id(self.camera.id, self.city2.id)
        self.assertIsNone(camera)
    
    def test_get_by_public_id(self):
        camera = self.repo.get_by_public_id(self.camera.public_id, self.city1.id)
        self.assertEqual(camera.id, self.camera.id)
    
    def test_list_by_city(self):
        cameras = self.repo.list_by_city(self.city1.id)
        self.assertEqual(len(cameras), 1)
        self.assertEqual(cameras[0].id, self.camera.id)
    
    def test_list_by_city_isolation(self):
        cameras = self.repo.list_by_city(self.city2.id)
        self.assertEqual(len(cameras), 0)
    
    def test_exists_with_correct_city(self):
        self.assertTrue(self.repo.exists(self.camera.id, self.city1.id))
    
    def test_exists_with_wrong_city(self):
        self.assertFalse(self.repo.exists(self.camera.id, self.city2.id))
    
    def test_count_by_city(self):
        self.assertEqual(self.repo.count_by_city(self.city1.id), 1)
        self.assertEqual(self.repo.count_by_city(self.city2.id), 0)
    
    def test_list_by_city_filter_active(self):
        self.camera.is_active = False
        self.camera.save()
        
        active = self.repo.list_by_city(self.city1.id, is_active=True)
        inactive = self.repo.list_by_city(self.city1.id, is_active=False)
        
        self.assertEqual(len(active), 0)
        self.assertEqual(len(inactive), 1)
