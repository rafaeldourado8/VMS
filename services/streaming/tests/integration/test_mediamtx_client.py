import pytest
from unittest.mock import patch, Mock
from infrastructure.mediamtx.mediamtx_client import MediaMTXClient


@patch('infrastructure.mediamtx.mediamtx_client.httpx')
def test_add_path_success(mock_httpx):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_httpx.patch.return_value = mock_response
    
    client = MediaMTXClient()
    result = client.add_path("cam_1", "rtsp://test.com")
    
    assert result is True
    mock_httpx.patch.assert_called_once()


@patch('infrastructure.mediamtx.mediamtx_client.httpx')
def test_add_path_failure(mock_httpx):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_httpx.patch.return_value = mock_response
    
    client = MediaMTXClient()
    result = client.add_path("cam_1", "rtsp://test.com")
    
    assert result is False


@patch('infrastructure.mediamtx.mediamtx_client.httpx')
def test_remove_path_success(mock_httpx):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_httpx.delete.return_value = mock_response
    
    client = MediaMTXClient()
    result = client.remove_path("cam_1")
    
    assert result is True


@patch('infrastructure.mediamtx.mediamtx_client.httpx')
def test_get_path_status_success(mock_httpx):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ready": True, "readers": 1}
    mock_httpx.get.return_value = mock_response
    
    client = MediaMTXClient()
    result = client.get_path_status("cam_1")
    
    assert result is not None
    assert result["ready"] is True


@patch('infrastructure.mediamtx.mediamtx_client.httpx')
def test_get_path_status_not_found(mock_httpx):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_httpx.get.return_value = mock_response
    
    client = MediaMTXClient()
    result = client.get_path_status("cam_999")
    
    assert result is None
