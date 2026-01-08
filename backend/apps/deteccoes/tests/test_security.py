import pytest

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.cameras.models import Camera
from apps.deteccoes.models import Deteccao

User = get_user_model()

@pytest.mark.django_db
class TestSecurityVulnerabilities:
    def setup_method(self):
        self.client = APIClient()
        # Cria um administrador para ter acesso total (pior cenário se houver falha)
        self.user = User.objects.create_superuser(email="admin@sec.com", name="Admin", password="123")
        self.camera = Camera.objects.create(owner=self.user, name="Cam1", stream_url="rtsp://test")
        
        # Dados legítimos
        Deteccao.objects.create(camera=self.camera, plate="ABC-1234", timestamp=timezone.now())
        
        self.client.force_authenticate(user=self.user)

    def test_sql_injection_search_parameter(self):
        """
        Tenta injetar SQL através de parâmetros de query string (ex: filtros de placa).
        O objetivo é garantir que o ORM escapa a string e não executa o comando.
        """
        # Payload clássico que tentaria tornar a condição sempre verdadeira
        payload_malicioso = "' OR 1=1 --"
        
        # Tenta filtrar detecções usando o payload
        response = self.client.get(f"/api/detections/?plate={payload_malicioso}")

        assert response.status_code == 200
        data = response.json()
        
        # Se a paginação estiver ativa, os dados estão em 'results'
        results = data.get('results', data)

        # O teste PASSA se a lista estiver vazia. 
        # Se falhar (SQL Injection bem sucedido), retornaria TODAS as placas.
        assert len(results) == 0 

    def test_stored_xss_prevention(self):
        """
        Verifica se a API permite persistir scripts maliciosos (Stored XSS).
        O Django DRF sanitiza na saída, mas é bom validar a entrada/saída.
        """
        xss_payload = "<script>alert('Hacked')</script>"
        
        # Tenta criar uma câmara com nome malicioso
        response = self.client.post("/api/cameras/", {
            "name": xss_payload,
            "stream_url": "rtsp://hacker",
            "location": "Lab"
        })

        # O Backend deve aceitar salvar (pois é texto), mas o Frontend (React) 
        # deve escapar isso automaticamente. O teste aqui garante que o servidor
        # não crashou ou executou o script no lado do servidor.
        assert response.status_code == 201
        assert response.data['name'] == xss_payload 
        # Nota: A proteção real contra a *execução* deste script está no React (frontend).