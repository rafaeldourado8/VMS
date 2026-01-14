import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domain.entities.recording import Recording

def test_recording_creation():
    recording = Recording(
        id='123',
        camera_id='cam-1',
        file_path='/recordings/cam-1/video.mp4',
        started_at=datetime.now()
    )
    
    assert recording.id == '123'
    assert recording.is_permanent is False

def test_recording_should_delete_expired():
    old_date = datetime.now() - timedelta(days=8)
    recording = Recording(
        id='1',
        camera_id='cam-1',
        file_path='/path',
        started_at=old_date
    )
    
    assert recording.should_delete(retention_days=7) is True
    assert recording.should_delete(retention_days=10) is False

def test_recording_permanent_not_deleted():
    old_date = datetime.now() - timedelta(days=100)
    recording = Recording(
        id='1',
        camera_id='cam-1',
        file_path='/path',
        started_at=old_date,
        is_permanent=True
    )
    
    assert recording.should_delete(retention_days=7) is False

def test_recording_expires_in_days():
    recent_date = datetime.now() - timedelta(days=5)
    recording = Recording(
        id='1',
        camera_id='cam-1',
        file_path='/path',
        started_at=recent_date
    )
    
    assert recording.expires_in_days(retention_days=7) == 2

def test_recording_mark_as_permanent():
    recording = Recording(
        id='1',
        camera_id='cam-1',
        file_path='/path',
        started_at=datetime.now()
    )
    
    recording.mark_as_permanent()
    assert recording.is_permanent is True
