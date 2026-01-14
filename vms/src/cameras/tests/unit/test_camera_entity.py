import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domain.entities.camera import Camera

def test_camera_creation_rtsp():
    camera = Camera(
        id='123',
        name='Camera LPR 1',
        stream_url='rtsp://example.com/stream',
        city_id='city-1'
    )
    
    assert camera.id == '123'
    assert camera.name == 'Camera LPR 1'
    assert camera.type == 'rtsp'
    assert camera.lpr_enabled is True
    assert camera.status == 'inactive'

def test_camera_creation_rtmp():
    camera = Camera(
        id='456',
        name='Camera Bullet 1',
        stream_url='rtmp://example.com/stream',
        city_id='city-1'
    )
    
    assert camera.type == 'rtmp'
    assert camera.lpr_enabled is False

def test_camera_invalid_url():
    with pytest.raises(ValueError, match="Invalid stream URL"):
        Camera(
            id='789',
            name='Invalid',
            stream_url='http://example.com',
            city_id='city-1'
        )

def test_camera_activate():
    camera = Camera(id='1', name='Cam', stream_url='rtsp://url', city_id='c1')
    camera.activate()
    assert camera.status == 'active'
    assert camera.is_active() is True

def test_camera_deactivate():
    camera = Camera(id='1', name='Cam', stream_url='rtsp://url', city_id='c1', status='active')
    camera.deactivate()
    assert camera.status == 'inactive'
    assert camera.is_active() is False

def test_camera_is_lpr_enabled():
    rtsp_camera = Camera(id='1', name='LPR', stream_url='rtsp://url', city_id='c1')
    rtmp_camera = Camera(id='2', name='Bullet', stream_url='rtmp://url', city_id='c1')
    
    assert rtsp_camera.is_lpr_enabled() is True
    assert rtmp_camera.is_lpr_enabled() is False
