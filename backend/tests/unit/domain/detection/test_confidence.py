import pytest
from domain.detection.value_objects.confidence import Confidence
from domain.detection.exceptions import InvalidConfidenceException


def test_valid_confidence():
    conf = Confidence(0.95)
    assert float(conf) == 0.95


def test_high_confidence():
    conf = Confidence(0.85)
    assert conf.is_high()
    assert not conf.is_low()


def test_low_confidence():
    conf = Confidence(0.45)
    assert conf.is_low()
    assert not conf.is_high()


def test_none_confidence():
    conf = Confidence(None)
    assert float(conf) == 0.0


def test_confidence_above_1_raises_exception():
    with pytest.raises(InvalidConfidenceException):
        Confidence(1.5)


def test_confidence_below_0_raises_exception():
    with pytest.raises(InvalidConfidenceException):
        Confidence(-0.1)


def test_confidence_is_immutable():
    conf = Confidence(0.8)
    with pytest.raises(Exception):
        conf.value = 0.9
