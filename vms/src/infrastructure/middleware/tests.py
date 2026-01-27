from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from uuid import uuid4
from shared.admin.cidades.models import City
from infrastructure.middleware import TenantMiddleware

class TenantMiddlewareTest(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TenantMiddleware(lambda r: None)
        self.city = City.objects.create(name="São Paulo")
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
    
    def test_public_path_bypasses_validation(self):
        request = self.factory.get('/admin/')
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
    
    def test_superuser_bypasses_validation(self):
        request = self.factory.get('/api/cameras/')
        request.user = self.superuser
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
    
    def test_missing_city_id_header(self):
        request = self.factory.get('/api/cameras/')
        request.user = User()
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn('X-City-ID header required', response.content.decode())
    
    def test_invalid_city_id_format(self):
        request = self.factory.get('/api/cameras/')
        request.user = User()
        request.META['HTTP_X_CITY_ID'] = 'invalid-uuid'
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid X-City-ID format', response.content.decode())
    
    def test_city_not_found(self):
        request = self.factory.get('/api/cameras/')
        request.user = User()
        request.META['HTTP_X_CITY_ID'] = str(uuid4())
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 404)
        self.assertIn('City not found', response.content.decode())
    
    def test_valid_city_id_injected(self):
        request = self.factory.get('/api/cameras/')
        request.user = User()
        request.META['HTTP_X_CITY_ID'] = str(self.city.id)
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
        self.assertEqual(request.city_id, self.city.id)
    
    def test_static_path_bypasses_validation(self):
        request = self.factory.get('/static/css/style.css')
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
    
    def test_health_path_bypasses_validation(self):
        request = self.factory.get('/health/')
        response = self.middleware.process_request(request)
        self.assertIsNone(response)
