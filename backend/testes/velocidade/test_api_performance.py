"""
Testes de Performance da API
"""
import pytest
import time
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestAPIPerformance:
    """Testes de performance da API"""

    def test_list_cameras_response_time(self, authenticated_client, multiple_cameras):
        """Teste tempo de resposta da listagem de câmeras"""
        url = reverse('camera-list')
        
        start = time.time()
        response = authenticated_client.get(url)
        end = time.time()
        
        response_time = (end - start) * 1000  # ms
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 200  # Menos de 200ms

    def test_retrieve_camera_response_time(self, authenticated_client, test_camera):
        """Teste tempo de resposta de recuperação de câmera"""
        url = reverse('camera-detail', kwargs={'pk': test_camera.id})
        
        start = time.time()
        response = authenticated_client.get(url)
        end = time.time()
        
        response_time = (end - start) * 1000
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 100  # Menos de 100ms

    def test_create_camera_response_time(self, authenticated_client):
        """Teste tempo de resposta de criação de câmera"""
        url = reverse('camera-list')
        data = {
            'nome': 'Performance Test Camera',
            'rtsp_url': 'rtsp://test@192.168.1.1:554/stream',
            'localizacao': 'Test',
            'ativa': True
        }
        
        start = time.time()
        response = authenticated_client.post(url, data, format='json')
        end = time.time()
        
        response_time = (end - start) * 1000
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response_time < 300  # Menos de 300ms

    def test_bulk_operations_performance(self, authenticated_client):
        """Teste performance de operações em massa"""
        url = reverse('camera-list')
        
        # Criar 50 câmeras
        start = time.time()
        for i in range(50):
            data = {
                'nome': f'Bulk Camera {i}',
                'rtsp_url': f'rtsp://test@192.168.1.{i}:554/stream',
                'localizacao': f'Location {i}',
                'ativa': True
            }
            authenticated_client.post(url, data, format='json')
        end = time.time()
        
        total_time = end - start
        avg_time = (total_time / 50) * 1000
        
        assert avg_time < 500  # Média menor que 500ms por operação

    def test_pagination_performance(self, authenticated_client, multiple_cameras):
        """Teste performance de paginação"""
        url = reverse('camera-list')
        
        start = time.time()
        response = authenticated_client.get(url, {'page': 1, 'page_size': 50})
        end = time.time()
        
        response_time = (end - start) * 1000
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 200

    def test_filter_performance(self, authenticated_client, multiple_cameras):
        """Teste performance de filtros"""
        url = reverse('camera-list')
        
        start = time.time()
        response = authenticated_client.get(url, {
            'ativa': True,
            'localizacao': 'Local 0'
        })
        end = time.time()
        
        response_time = (end - start) * 1000
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 150

    def test_search_performance(self, authenticated_client, multiple_cameras):
        """Teste performance de busca"""
        url = reverse('camera-list')
        
        start = time.time()
        response = authenticated_client.get(url, {'search': 'Camera'})
        end = time.time()
        
        response_time = (end - start) * 1000
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 250


@pytest.mark.django_db
class TestDatabasePerformance:
    """Testes de performance do banco de dados"""

    def test_query_count_list_cameras(self, authenticated_client, multiple_cameras, django_assert_num_queries):
        """Teste número de queries na listagem"""
        url = reverse('camera-list')
        
        # Deve fazer no máximo 5 queries (otimizado com select_related/prefetch_related)
        with django_assert_num_queries(5):
            authenticated_client.get(url)

    def test_n_plus_one_problem(self, authenticated_client, multiple_cameras, django_assert_num_queries):
        """Teste problema N+1"""
        url = reverse('camera-list')
        
        # Número de queries não deve crescer linearmente com número de câmeras
        with django_assert_num_queries(5):  # Fixo, não N+1
            authenticated_client.get(url)
