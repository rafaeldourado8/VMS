import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domain.entities.blacklist_entry import BlacklistEntry

def test_blacklist_entry_creation():
    entry = BlacklistEntry(
        id='123',
        plate='ABC1234',
        reason='Stolen vehicle',
        city_id='city-1',
        created_at=datetime.now()
    )
    
    assert entry.id == '123'
    assert entry.plate == 'ABC1234'
    assert entry.is_active is True

def test_blacklist_entry_matches():
    entry = BlacklistEntry(
        id='1', plate='ABC1234', reason='Test',
        city_id='c1', created_at=datetime.now()
    )
    
    assert entry.matches('ABC1234') is True
    assert entry.matches('abc1234') is True  # Case insensitive
    assert entry.matches('XYZ5678') is False

def test_blacklist_entry_inactive_not_matches():
    entry = BlacklistEntry(
        id='1', plate='ABC1234', reason='Test',
        city_id='c1', created_at=datetime.now(), is_active=False
    )
    
    assert entry.matches('ABC1234') is False

def test_blacklist_entry_deactivate():
    entry = BlacklistEntry(
        id='1', plate='ABC1234', reason='Test',
        city_id='c1', created_at=datetime.now()
    )
    
    entry.deactivate()
    assert entry.is_active is False
