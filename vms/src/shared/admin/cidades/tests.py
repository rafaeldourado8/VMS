from django.test import TestCase
from shared.admin.cidades.models import City
from shared.admin.cidades.enums import CityStatus, Plan

class CityModelTest(TestCase):
    
    def test_create_city(self):
        city = City.objects.create(
            name="São Paulo",
            status=CityStatus.ACTIVE,
            plan=Plan.PREMIUM
        )
        self.assertIsNotNone(city.id)
        self.assertEqual(city.name, "São Paulo")
        self.assertEqual(city.status, CityStatus.ACTIVE)
        self.assertEqual(city.plan, Plan.PREMIUM)
    
    def test_city_uuid_primary_key(self):
        city = City.objects.create(name="Rio de Janeiro")
        self.assertEqual(len(str(city.id)), 36)
    
    def test_city_default_status(self):
        city = City.objects.create(name="Belo Horizonte")
        self.assertEqual(city.status, CityStatus.ACTIVE)
    
    def test_city_default_plan(self):
        city = City.objects.create(name="Curitiba")
        self.assertEqual(city.plan, Plan.BASIC)
    
    def test_city_is_active(self):
        city = City.objects.create(name="Porto Alegre", status=CityStatus.ACTIVE)
        self.assertTrue(city.is_active())
        
        city.status = CityStatus.INACTIVE
        city.save()
        self.assertFalse(city.is_active())
    
    def test_city_unique_name(self):
        City.objects.create(name="Salvador")
        with self.assertRaises(Exception):
            City.objects.create(name="Salvador")
    
    def test_city_str_representation(self):
        city = City.objects.create(name="Fortaleza")
        self.assertEqual(str(city), "Fortaleza")
