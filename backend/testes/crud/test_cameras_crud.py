"""
Testes CRUD para Câmeras
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestCamerasCRUD:
    """Testes de CRUD para câmeras"""

    def test_create_camera(self, authenticated_client):
        """Teste criação de câmera"""
        url = reverse('camera-list')
        data = {
            'nome': 'Nova Camera',
            'rtsp_url': 'rtsp://admin:pass@192.168.1.50:554/stream1',
            'localizacao': 'Entrada',
            'ativa': True
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['nome'] == 'Nova Camera'

    def test_list_cameras(self, authenticated_client, test_camera):
        """Teste listagem de câmeras"""
        url = reverse('camera-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_retrieve_camera(self, authenticated_client, test_camera):
        """Teste recuperação de câmera específica"""
        url = reverse('camera-detail', kwargs={'pk': test_camera.id})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nome'] == test_camera.nome

    def test_update_camera(self, authenticated_client, test_camera):
        """Teste atualização de câmera"""
        url = reverse('camera-detail', kwargs={'pk': test_camera.id})
        data = {'nome': 'Camera Atualizada'}
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nome'] == 'Camera Atualizada'

    def test_delete_camera(self, authenticated_client, test_camera):
        """Teste exclusão de câmera"""
        url = reverse('camera-detail', kwargs={'pk': test_camera.id})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_filter_cameras_by_location(self, authenticated_client, multiple_cameras):
        """Teste filtro por localização"""
        url = reverse('camera-list')
        response = authenticated_client.get(url, {'localizacao': 'Local 0'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_filter_cameras_by_active(self, authenticated_client, multiple_cameras):
        """Teste filtro por status ativo"""
        url = reverse('camera-list')
        response = authenticated_client.get(url, {'ativa': True})
        assert response.status_code == status.HTTP_200_OK
        assert all(cam['ativa'] for cam in response.data['results'])
