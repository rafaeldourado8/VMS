import pytest
from domain.detection.entities.vehicle import Vehicle
from domain.detection.value_objects.bounding_box import BoundingBox


def test_create_vehicle():
    bbox = BoundingBox(x=100, y=100, width=50, height=80)
    vehicle = Vehicle(track_id=1, bbox=bbox, confidence=0.95)
    
    assert vehicle.track_id == 1
    assert vehicle.confidence == 0.95


def test_update_position():
    bbox1 = BoundingBox(x=100, y=100, width=50, height=80)
    vehicle = Vehicle(track_id=1, bbox=bbox1, confidence=0.95)
    
    bbox2 = BoundingBox(x=110, y=110, width=50, height=80)
    vehicle.update_position(bbox2)
    
    assert vehicle.bbox == bbox2
    assert len(vehicle.positions) == 1


def test_mark_crossed_p1():
    bbox = BoundingBox(x=100, y=100, width=50, height=80)
    vehicle = Vehicle(track_id=1, bbox=bbox, confidence=0.95)
    
    vehicle.mark_crossed_p1()
    
    assert vehicle.crossed_p1


def test_mark_crossed_p2():
    bbox = BoundingBox(x=100, y=100, width=50, height=80)
    vehicle = Vehicle(track_id=1, bbox=bbox, confidence=0.95)
    
    vehicle.mark_crossed_p2()
    
    assert vehicle.crossed_p2


def test_set_plate():
    bbox = BoundingBox(x=100, y=100, width=50, height=80)
    vehicle = Vehicle(track_id=1, bbox=bbox, confidence=0.95)
    
    vehicle.set_plate("ABC1234", 0.92)
    
    assert vehicle.has_plate()
    assert vehicle.plate == "ABC1234"


def test_is_ready_for_trigger():
    bbox = BoundingBox(x=100, y=100, width=50, height=80)
    vehicle = Vehicle(track_id=1, bbox=bbox, confidence=0.95)
    
    assert not vehicle.is_ready_for_trigger()
    
    vehicle.mark_crossed_p1()
    assert vehicle.is_ready_for_trigger()
    
    vehicle.mark_crossed_p2()
    assert not vehicle.is_ready_for_trigger()
