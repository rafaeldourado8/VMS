import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domain.entities.vehicle_search import VehicleSearch

def test_vehicle_search_creation():
    search = VehicleSearch(
        id='123',
        city_id='city-1',
        user_id='user-1',
        plate='ABC1234',
        color='red',
        vehicle_type='car',
        start_date=datetime.now(),
        end_date=datetime.now()
    )
    
    assert search.id == '123'
    assert search.plate == 'ABC1234'
    assert search.status == 'pending'

def test_vehicle_search_start_processing():
    search = VehicleSearch(
        id='1', city_id='c1', user_id='u1',
        plate='ABC1234', color=None, vehicle_type=None,
        start_date=datetime.now(), end_date=datetime.now()
    )
    
    search.start_processing()
    assert search.status == 'processing'

def test_vehicle_search_complete():
    search = VehicleSearch(
        id='1', city_id='c1', user_id='u1',
        plate='ABC1234', color=None, vehicle_type=None,
        start_date=datetime.now(), end_date=datetime.now()
    )
    
    search.complete()
    assert search.status == 'completed'
    assert search.is_completed() is True

def test_vehicle_search_fail():
    search = VehicleSearch(
        id='1', city_id='c1', user_id='u1',
        plate='ABC1234', color=None, vehicle_type=None,
        start_date=datetime.now(), end_date=datetime.now()
    )
    
    search.fail("Test error")
    assert search.status == 'failed'
    assert search.error_message == "Test error"
