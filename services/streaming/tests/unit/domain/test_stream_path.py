import pytest
from domain.streaming.value_objects.stream_path import StreamPath
from domain.streaming.exceptions import InvalidStreamPathException


def test_valid_stream_path():
    path = StreamPath(camera_id=1)
    assert str(path) == "cam_1"


def test_stream_path_with_large_id():
    path = StreamPath(camera_id=999)
    assert str(path) == "cam_999"


def test_invalid_camera_id_raises_exception():
    with pytest.raises(InvalidStreamPathException):
        StreamPath(camera_id=0)


def test_negative_camera_id_raises_exception():
    with pytest.raises(InvalidStreamPathException):
        StreamPath(camera_id=-1)


def test_stream_path_is_immutable():
    path = StreamPath(camera_id=1)
    with pytest.raises(Exception):
        path.camera_id = 2
