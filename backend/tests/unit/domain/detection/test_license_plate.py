import pytest
from domain.detection.value_objects.license_plate import LicensePlate
from domain.detection.exceptions import InvalidLicensePlateException


def test_valid_old_format_plate():
    plate = LicensePlate("ABC1234")
    assert str(plate) == "ABC1234"


def test_valid_mercosul_format_plate():
    plate = LicensePlate("ABC1D23")
    assert str(plate) == "ABC1D23"


def test_normalize_plate_with_hyphen():
    plate = LicensePlate("ABC-1234")
    assert str(plate) == "ABC1234"


def test_normalize_lowercase_plate():
    plate = LicensePlate("abc1234")
    assert str(plate) == "ABC1234"


def test_invalid_length_raises_exception():
    with pytest.raises(InvalidLicensePlateException):
        LicensePlate("AB123")


def test_invalid_format_raises_exception():
    with pytest.raises(InvalidLicensePlateException):
        LicensePlate("1234ABC")


def test_none_plate():
    plate = LicensePlate(None)
    assert str(plate) == ""


def test_plate_is_immutable():
    plate = LicensePlate("ABC1234")
    with pytest.raises(Exception):
        plate.value = "XYZ9999"
