import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domain.value_objects.search_criteria import SearchCriteria

def test_search_criteria_creation():
    criteria = SearchCriteria(plate='ABC1234', color='red', vehicle_type='car')
    
    assert criteria.plate == 'ABC1234'
    assert criteria.color == 'red'
    assert criteria.vehicle_type == 'car'

def test_search_criteria_has_plate():
    with_plate = SearchCriteria(plate='ABC1234')
    without_plate = SearchCriteria(plate=None)
    empty_plate = SearchCriteria(plate='')
    
    assert with_plate.has_plate() is True
    assert without_plate.has_plate() is False
    assert empty_plate.has_plate() is False

def test_search_criteria_has_color():
    with_color = SearchCriteria(color='red')
    without_color = SearchCriteria(color=None)
    
    assert with_color.has_color() is True
    assert without_color.has_color() is False

def test_search_criteria_has_vehicle_type():
    with_type = SearchCriteria(vehicle_type='car')
    without_type = SearchCriteria(vehicle_type=None)
    
    assert with_type.has_vehicle_type() is True
    assert without_type.has_vehicle_type() is False

def test_search_criteria_is_empty():
    empty = SearchCriteria()
    with_plate = SearchCriteria(plate='ABC1234')
    with_color = SearchCriteria(color='red')
    
    assert empty.is_empty() is True
    assert with_plate.is_empty() is False
    assert with_color.is_empty() is False

def test_search_criteria_immutable():
    criteria = SearchCriteria(plate='ABC1234')
    
    with pytest.raises(Exception):
        criteria.plate = 'XYZ5678'
