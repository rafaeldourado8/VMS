import pytest
from infrastructure.repositories.in_memory_stream_repository import InMemoryStreamRepository
from domain.streaming.entities.stream import Stream
from domain.streaming.value_objects.stream_path import StreamPath
from domain.streaming.value_objects.hls_url import HLSUrl


def test_save_and_find_stream():
    repo = InMemoryStreamRepository()
    
    stream = Stream(
        camera_id=1,
        rtsp_url="rtsp://test.com",
        path=StreamPath(1),
        hls_url=HLSUrl("http://localhost:8889", "cam_1")
    )
    
    saved = repo.save(stream)
    found = repo.find_by_camera(1)
    
    assert found is not None
    assert found.camera_id == 1


def test_find_all_streams():
    repo = InMemoryStreamRepository()
    
    stream1 = Stream(
        camera_id=1,
        rtsp_url="rtsp://test1.com",
        path=StreamPath(1),
        hls_url=HLSUrl("http://localhost:8889", "cam_1")
    )
    stream2 = Stream(
        camera_id=2,
        rtsp_url="rtsp://test2.com",
        path=StreamPath(2),
        hls_url=HLSUrl("http://localhost:8889", "cam_2")
    )
    
    repo.save(stream1)
    repo.save(stream2)
    
    all_streams = repo.find_all()
    
    assert len(all_streams) == 2


def test_delete_stream():
    repo = InMemoryStreamRepository()
    
    stream = Stream(
        camera_id=1,
        rtsp_url="rtsp://test.com",
        path=StreamPath(1),
        hls_url=HLSUrl("http://localhost:8889", "cam_1")
    )
    
    repo.save(stream)
    repo.delete(1)
    
    found = repo.find_by_camera(1)
    assert found is None


def test_exists_stream():
    repo = InMemoryStreamRepository()
    
    stream = Stream(
        camera_id=1,
        rtsp_url="rtsp://test.com",
        path=StreamPath(1),
        hls_url=HLSUrl("http://localhost:8889", "cam_1")
    )
    
    repo.save(stream)
    
    assert repo.exists(1)
    assert not repo.exists(999)
