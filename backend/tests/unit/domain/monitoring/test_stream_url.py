import pytest
from domain.monitoring.value_objects.stream_url import StreamUrl
from domain.monitoring.exceptions import InvalidStreamUrlException


def test_valid_rtsp_url():
    url = StreamUrl("rtsp://192.168.1.100:554/stream")
    assert str(url) == "rtsp://192.168.1.100:554/stream"


def test_valid_http_url():
    url = StreamUrl("http://example.com/stream")
    assert str(url) == "http://example.com/stream"


def test_empty_url_raises_exception():
    with pytest.raises(InvalidStreamUrlException, match="URL não pode ser vazia"):
        StreamUrl("")


def test_invalid_protocol_raises_exception():
    with pytest.raises(InvalidStreamUrlException, match="deve começar com"):
        StreamUrl("ftp://invalid.com")


def test_stream_url_is_immutable():
    url = StreamUrl("rtsp://test.com")
    with pytest.raises(Exception):
        url.value = "rtsp://other.com"
