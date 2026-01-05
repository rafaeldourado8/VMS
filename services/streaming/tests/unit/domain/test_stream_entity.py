import pytest
from domain.streaming.entities.stream import Stream, StreamStatus
from domain.streaming.value_objects.stream_path import StreamPath
from domain.streaming.value_objects.hls_url import HLSUrl


def test_create_stream():
    stream = Stream(
        camera_id=1,
        rtsp_url="rtsp://test.com",
        path=StreamPath(1),
        hls_url=HLSUrl("http://localhost:8889", "cam_1")
    )
    assert stream.camera_id == 1
    assert stream.status == StreamStatus.INACTIVE


def test_start_stream():
    stream = Stream(
        camera_id=1,
        rtsp_url="rtsp://test.com",
        path=StreamPath(1),
        hls_url=HLSUrl("http://localhost:8889", "cam_1")
    )
    stream.start()
    assert stream.is_active()


def test_stop_stream():
    stream = Stream(
        camera_id=1,
        rtsp_url="rtsp://test.com",
        path=StreamPath(1),
        hls_url=HLSUrl("http://localhost:8889", "cam_1")
    )
    stream.start()
    stream.stop()
    assert not stream.is_active()
    assert stream.viewers == 0


def test_mark_error():
    stream = Stream(
        camera_id=1,
        rtsp_url="rtsp://test.com",
        path=StreamPath(1),
        hls_url=HLSUrl("http://localhost:8889", "cam_1")
    )
    stream.mark_error()
    assert stream.status == StreamStatus.ERROR


def test_add_viewer():
    stream = Stream(
        camera_id=1,
        rtsp_url="rtsp://test.com",
        path=StreamPath(1),
        hls_url=HLSUrl("http://localhost:8889", "cam_1")
    )
    stream.add_viewer()
    stream.add_viewer()
    assert stream.viewers == 2


def test_remove_viewer():
    stream = Stream(
        camera_id=1,
        rtsp_url="rtsp://test.com",
        path=StreamPath(1),
        hls_url=HLSUrl("http://localhost:8889", "cam_1")
    )
    stream.add_viewer()
    stream.add_viewer()
    stream.remove_viewer()
    assert stream.viewers == 1


def test_remove_viewer_does_not_go_negative():
    stream = Stream(
        camera_id=1,
        rtsp_url="rtsp://test.com",
        path=StreamPath(1),
        hls_url=HLSUrl("http://localhost:8889", "cam_1")
    )
    stream.remove_viewer()
    assert stream.viewers == 0
