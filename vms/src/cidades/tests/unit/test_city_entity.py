import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domain.entities.city import City

def test_city_creation():
    city = City(
        id='123',
        name='São Paulo',
        slug='sao_paulo',
        plan='basic'
    )
    
    assert city.id == '123'
    assert city.name == 'São Paulo'
    assert city.slug == 'sao_paulo'
    assert city.plan == 'basic'
    assert city.max_cameras == 1000
    assert city.max_lpr_cameras == 20

def test_city_retention_days():
    basic = City(id='1', name='City', slug='city', plan='basic')
    pro = City(id='2', name='City', slug='city', plan='pro')
    premium = City(id='3', name='City', slug='city', plan='premium')
    
    assert basic.retention_days == 7
    assert pro.retention_days == 15
    assert premium.retention_days == 30

def test_city_max_users():
    basic = City(id='1', name='City', slug='city', plan='basic')
    pro = City(id='2', name='City', slug='city', plan='pro')
    premium = City(id='3', name='City', slug='city', plan='premium')
    
    assert basic.max_users == 3
    assert pro.max_users == 5
    assert premium.max_users == 10

def test_can_add_camera():
    city = City(id='1', name='City', slug='city', plan='basic')
    
    assert city.can_add_camera(999) is True
    assert city.can_add_camera(1000) is False
    assert city.can_add_camera(1001) is False

def test_can_add_lpr_camera():
    city = City(id='1', name='City', slug='city', plan='basic')
    
    assert city.can_add_lpr_camera(19) is True
    assert city.can_add_lpr_camera(20) is False
    assert city.can_add_lpr_camera(21) is False
