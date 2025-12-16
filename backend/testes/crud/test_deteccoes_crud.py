"""
Testes CRUD para Detecções
"""
import pytest
from django.urls import reverse
from rest_framework import status
from datetime import datetime, timedelta


@pytest.mark.django_db
class TestDeteccoesCRUD:
    """Testes de CRUD para detecções"""

    def test_create_deteccao(self, authenticated_client, test_camera):
        """Teste criação de detecção"""
        url = reverse('deteccao-list')
        data = {
            'camera': test_camera.id,
            'tipo_objeto': 'pessoa',
            'confianca': 0.95,
            'bbox_x': 100,
            'bbox_y': 100,
            'bbox_width': 200,
            'bbox_height': 300
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['tipo_objeto'] == 'pessoa'

    def test_list_deteccoes(self, authenticated_client, test_camera):
        """Teste listagem de detecções"""
        url = reverse('deteccao-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_filter_deteccoes_by_camera(self, authenticated_client, test_camera):
        """Teste filtro por câmera"""
        url = reverse('deteccao-list')
        response = authenticated_client.get(url, {'camera': test_camera.id})
        assert response.status_code == status.HTTP_200_OK

    def test_filter_deteccoes_by_date_range(self, authenticated_client):
        """Teste filtro por intervalo de datas"""
        url = reverse('deteccao-list')
        start = (datetime.now() - timedelta(days=7)).isoformat()
        end = datetime.now().isoformat()
        response = authenticated_client.get(url, {
            'timestamp_after': start,
            'timestamp_before': end
        })
        assert response.status_code == status.HTTP_200_OK

    def test_filter_deteccoes_by_tipo(self, authenticated_client):
        """Teste filtro por tipo de objeto"""
        url = reverse('deteccao-list')
        response = authenticated_client.get(url, {'tipo_objeto': 'pessoa'})
        assert response.status_code == status.HTTP_200_OK
