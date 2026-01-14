import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domain.entities.detection import Detection

def test_detection_creation():
    detection = Detection(
        id='123',
        camera_id='cam-1',
        plate='ABC1234',
        confidence=0.95,
        image_url='/detections/123.jpg',
        detected_at=datetime.now(),
        city_id='city-1'
    )
    
    assert detection.id == '123'
    assert detection.plate == 'ABC1234'
    assert detection.confidence == 0.95

def test_detection_is_high_confidence():
    high = Detection(
        id='1', camera_id='c1', plate='ABC1234',
        confidence=0.95, image_url='/img', detected_at=datetime.now(), city_id='c1'
    )
    low = Detection(
        id='2', camera_id='c1', plate='XYZ5678',
        confidence=0.80, image_url='/img', detected_at=datetime.now(), city_id='c1'
    )
    
    assert high.is_high_confidence() is True
    assert low.is_high_confidence() is False

def test_detection_is_valid_confidence():
    valid = Detection(
        id='1', camera_id='c1', plate='ABC1234',
        confidence=0.75, image_url='/img', detected_at=datetime.now(), city_id='c1'
    )
    invalid = Detection(
        id='2', camera_id='c1', plate='XYZ5678',
        confidence=0.70, image_url='/img', detected_at=datetime.now(), city_id='c1'
    )
    
    assert valid.is_valid_confidence() is True
    assert invalid.is_valid_confidence() is False
