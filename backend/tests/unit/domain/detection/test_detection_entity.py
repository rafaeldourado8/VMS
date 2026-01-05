import pytest
from datetime import datetime
from domain.detection.entities.detection import Detection
from domain.detection.value_objects.license_plate import LicensePlate
from domain.detection.value_objects.confidence import Confidence
from domain.detection.value_objects.vehicle_type import VehicleType


def test_create_detection():
    detection = Detection(
        id=1,
        camera_id=100,
        plate=LicensePlate("ABC1234"),
        confidence=Confidence(0.95),
        timestamp=datetime.now(),
        vehicle_type=VehicleType.CAR
    )
    assert detection.id == 1
    assert detection.camera_id == 100
    assert detection.vehicle_type == VehicleType.CAR


def test_is_high_confidence():
    detection = Detection(
        id=1,
        camera_id=100,
        plate=LicensePlate("ABC1234"),
        confidence=Confidence(0.92),
        timestamp=datetime.now()
    )
    assert detection.is_high_confidence()


def test_is_not_high_confidence():
    detection = Detection(
        id=1,
        camera_id=100,
        plate=LicensePlate("ABC1234"),
        confidence=Confidence(0.65),
        timestamp=datetime.now()
    )
    assert not detection.is_high_confidence()


def test_has_plate():
    detection = Detection(
        id=1,
        camera_id=100,
        plate=LicensePlate("ABC1234"),
        confidence=Confidence(0.95),
        timestamp=datetime.now()
    )
    assert detection.has_plate()


def test_has_no_plate():
    detection = Detection(
        id=1,
        camera_id=100,
        plate=LicensePlate(None),
        confidence=Confidence(0.95),
        timestamp=datetime.now()
    )
    assert not detection.has_plate()


def test_has_evidence_with_image():
    detection = Detection(
        id=1,
        camera_id=100,
        plate=LicensePlate("ABC1234"),
        confidence=Confidence(0.95),
        timestamp=datetime.now(),
        image_url="http://example.com/image.jpg"
    )
    assert detection.has_evidence()


def test_has_no_evidence():
    detection = Detection(
        id=1,
        camera_id=100,
        plate=LicensePlate("ABC1234"),
        confidence=Confidence(0.95),
        timestamp=datetime.now()
    )
    assert not detection.has_evidence()
