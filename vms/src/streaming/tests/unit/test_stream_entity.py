import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domain.entities.stream import Stream

def test_stream_creation():
    stream = Stream(
        id='123',
        camera_id='cam-1',
        hls_url='http://mediamtx:8888/camera_cam-1/index.m3u8'
    )
    
    assert stream.id == '123'
    assert stream.camera_id == 'cam-1'
    assert stream.status == 'stopped'
    assert stream.is_active() is False

def test_stream_start():
    stream = Stream(id='1', camera_id='cam-1', hls_url='http://url')
    stream.start()
    
    assert stream.status == 'active'
    assert stream.is_active() is True
    assert stream.started_at is not None

def test_stream_stop():
    stream = Stream(id='1', camera_id='cam-1', hls_url='http://url', status='active')
    stream.stop()
    
    assert stream.status == 'stopped'
    assert stream.is_active() is False
