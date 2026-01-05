import pytest
from domain.detection.value_objects.point import Point
from domain.detection.exceptions import InvalidPointException


def test_valid_point():
    point = Point(x=100.0, y=200.0)
    assert point.x == 100.0
    assert point.y == 200.0


def test_negative_x_raises_exception():
    with pytest.raises(InvalidPointException):
        Point(x=-10.0, y=100.0)


def test_negative_y_raises_exception():
    with pytest.raises(InvalidPointException):
        Point(x=100.0, y=-10.0)


def test_distance_to():
    p1 = Point(x=0.0, y=0.0)
    p2 = Point(x=3.0, y=4.0)
    assert p1.distance_to(p2) == 5.0


def test_point_is_immutable():
    point = Point(x=10.0, y=20.0)
    with pytest.raises(Exception):
        point.x = 30.0
