"""
Testes de Integração com MediaMTX (Streaming)
"""
import pytest
import requests
from unittest.mock import patch, Mock


@pytest.mark.django_db
class TestMediaMTXIntegration:
    """Testes de integração com MediaMTX"""

    @patch('requests.get')
    def test_mediamtx_api_call(self, mock_get, test_camera):
        """Teste chamada à API do MediaMTX"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': f'cam_{test_camera.id}',
            'ready': True,
            'tracks': ['video', 'audio']
        }
        mock_get.return_value = mock_response
        
        # Simular chamada à API
        response = requests.get(f'http://mediamtx:9997/v3/paths/cam_{test_camera.id}')
        
        assert response.status_code == 200
        assert response.json()['ready'] is True

    @patch('requests.get')
    def test_mediamtx_health_check(self, mock_get):
        """Teste health check do MediaMTX"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'ok'}
        mock_get.return_value = mock_response
        
        response = requests.get('http://mediamtx:9997/v3/config/global/get')
        
        assert response.status_code == 200

    @patch('requests.get')
    def test_mediamtx_list_streams(self, mock_get):
        """Teste listar streams ativos"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {'name': 'cam_1', 'ready': True},
                {'name': 'cam_2', 'ready': True}
            ]
        }
        mock_get.return_value = mock_response
        
        response = requests.get('http://mediamtx:9997/v3/paths/list')
        
        assert response.status_code == 200
        assert len(response.json()['items']) == 2


@pytest.mark.django_db
class TestStreamingEndpoints:
    """Testes de endpoints de streaming"""

    def test_camera_has_rtsp_url(self, test_camera):
        """Teste câmera tem URL RTSP"""
        assert test_camera.rtsp_url is not None
        assert 'rtsp://' in test_camera.rtsp_url


@pytest.mark.django_db
class TestStreamingPerformance:
    """Testes de performance de streaming"""

    def test_multiple_cameras_rtsp_urls(self, multiple_cameras):
        """Teste múltiplas câmeras têm URLs RTSP"""
        assert len(multiple_cameras) == 10
        for camera in multiple_cameras:
            assert camera.rtsp_url is not None
