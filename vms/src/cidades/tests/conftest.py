import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from domain.entities.city import City

@pytest.fixture
def sample_city():
    return City(
        id='test-id',
        name='Test City',
        slug='test_city',
        plan='basic'
    )

@pytest.fixture
def sample_cities():
    return [
        City(id='1', name='São Paulo', slug='sao_paulo', plan='basic'),
        City(id='2', name='Rio de Janeiro', slug='rio_de_janeiro', plan='pro'),
        City(id='3', name='Belo Horizonte', slug='belo_horizonte', plan='premium')
    ]
