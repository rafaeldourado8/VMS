import pytest
from domain.streaming.value_objects.hls_url import HLSUrl


def test_hls_url_generation():
    url = HLSUrl(base_url="http://localhost:8889", path="cam_1")
    assert str(url) == "http://localhost:8889/cam_1/index.m3u8"


def test_hls_url_with_different_base():
    url = HLSUrl(base_url="http://streaming:8889", path="cam_100")
    assert str(url) == "http://streaming:8889/cam_100/index.m3u8"


def test_hls_url_is_immutable():
    url = HLSUrl(base_url="http://localhost:8889", path="cam_1")
    with pytest.raises(Exception):
        url.path = "cam_2"
