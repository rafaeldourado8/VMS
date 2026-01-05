import pytest
from domain.monitoring.value_objects.geo_coordinates import GeoCoordinates
from domain.monitoring.exceptions import InvalidCoordinatesException


def test_valid_coordinates():
    coords = GeoCoordinates(latitude=-23.5505, longitude=-46.6333)
    assert coords.latitude == -23.5505
    assert coords.longitude == -46.6333
    assert coords.is_valid()


def test_none_coordinates():
    coords = GeoCoordinates(None, None)
    assert not coords.is_valid()


def test_invalid_latitude_raises_exception():
    with pytest.raises(InvalidCoordinatesException, match="Latitude deve estar entre"):
        GeoCoordinates(latitude=91.0, longitude=0.0)


def test_invalid_longitude_raises_exception():
    with pytest.raises(InvalidCoordinatesException, match="Longitude deve estar entre"):
        GeoCoordinates(latitude=0.0, longitude=181.0)


def test_coordinates_are_immutable():
    coords = GeoCoordinates(-23.5505, -46.6333)
    with pytest.raises(Exception):
        coords.latitude = 0.0
