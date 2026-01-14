import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domain.value_objects.city_slug import CitySlug

def test_valid_slug():
    slug = CitySlug('sao_paulo')
    assert slug.value == 'sao_paulo'
    assert str(slug) == 'sao_paulo'

def test_slug_with_numbers():
    slug = CitySlug('cidade123')
    assert slug.value == 'cidade123'

def test_slug_with_hyphen():
    slug = CitySlug('rio-de-janeiro')
    assert slug.value == 'rio-de-janeiro'

def test_empty_slug():
    with pytest.raises(ValueError, match="Slug cannot be empty"):
        CitySlug('')

def test_slug_with_uppercase():
    with pytest.raises(ValueError, match="must contain only lowercase"):
        CitySlug('SaoPaulo')

def test_slug_with_spaces():
    with pytest.raises(ValueError, match="must contain only lowercase"):
        CitySlug('sao paulo')

def test_slug_too_long():
    with pytest.raises(ValueError, match="must be 50 characters or less"):
        CitySlug('a' * 51)

def test_slug_immutable():
    slug = CitySlug('test')
    with pytest.raises(Exception):
        slug.value = 'changed'
