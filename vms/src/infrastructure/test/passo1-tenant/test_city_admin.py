from django.test import TestCase, Client
from django.contrib.auth.models import User
from shared.admin.cidades.models import City
from shared.admin.cidades.enums import CityStatus, Plan

class CityAdminTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
    
    def test_city_admin_list_view(self):
        City.objects.create(name="Test City 1")
        City.objects.create(name="Test City 2")
        
        response = self.client.get('/admin/cidades/city/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test City 1")
        self.assertContains(response, "Test City 2")
    
    def test_city_admin_add_view(self):
        response = self.client.get('/admin/cidades/city/add/')
        self.assertEqual(response.status_code, 200)
    
    def test_city_admin_create(self):
        response = self.client.post('/admin/cidades/city/add/', {
            'name': 'New City',
            'status': CityStatus.ACTIVE,
            'plan': Plan.STANDARD
        })
        self.assertEqual(City.objects.filter(name='New City').count(), 1)
