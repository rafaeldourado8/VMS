import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domain.value_objects.confidence import Confidence

def test_confidence_creation():
    conf = Confidence(0.95)
    assert conf.value == 0.95

def test_confidence_invalid_value():
    with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
        Confidence(1.5)
    
    with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
        Confidence(-0.1)

def test_confidence_is_high():
    high = Confidence(0.95)
    low = Confidence(0.85)
    
    assert high.is_high() is True
    assert low.is_high() is False

def test_confidence_is_valid():
    valid = Confidence(0.75)
    invalid = Confidence(0.70)
    
    assert valid.is_valid() is True
    assert invalid.is_valid() is False

def test_confidence_str():
    conf = Confidence(0.95)
    assert str(conf) == "95.00%"

def test_confidence_immutable():
    conf = Confidence(0.95)
    with pytest.raises(Exception):
        conf.value = 0.80
