import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from infrastructure.persistence.django.models import SectorModel, AuditLogModel
from apps.cameras.models import Camera

User = get_user_model()


@pytest.fixture
def sector_a():
    return SectorModel.objects.create(name="Setor A", description="Departamento A")


@pytest.fixture
def sector_b():
    return SectorModel.objects.create(name="Setor B", description="Departamento B")


@pytest.fixture
def user_sector_a(sector_a):
    user = User.objects.create_user(email="user_a@test.com", name="User A", password="testpass123")
    user.sectors.add(sector_a)
    return user


@pytest.fixture
def user_sector_b(sector_b):
    user = User.objects.create_user(email="user_b@test.com", name="User B", password="testpass123")
    user.sectors.add(sector_b)
    return user


@pytest.fixture
def camera_sector_a(user_sector_a, sector_a):
    return Camera.objects.create(
        owner=user_sector_a,
        sector=sector_a,
        name="Camera Setor A",
        stream_url="rtsp://test:test@192.168.1.100/stream",
        location="Entrada A"
    )


@pytest.fixture
def camera_sector_b(user_sector_b, sector_b):
    return Camera.objects.create(
        owner=user_sector_b,
        sector=sector_b,
        name="Camera Setor B",
        stream_url="rtsp://test:test@192.168.1.101/stream",
        location="Entrada B"
    )


@pytest.mark.django_db
class TestBrokenAccessControl:
    """A01: Broken Access Control - OWASP Top 10"""

    def test_user_only_sees_own_sector_cameras(self, user_sector_a, camera_sector_a, camera_sector_b):
        """Usuário do Setor A não deve ver câmeras do Setor B"""
        client = APIClient()
        client.force_authenticate(user=user_sector_a)
        
        response = client.get('/api/cameras/')
        
        assert response.status_code == 200
        camera_ids = [cam['id'] for cam in response.data.get('results', response.data)]
        assert camera_sector_a.id in camera_ids
        assert camera_sector_b.id not in camera_ids

    def test_user_cannot_access_other_sector_camera(self, user_sector_a, camera_sector_b):
        """Usuário do Setor A não pode acessar detalhes de câmera do Setor B"""
        client = APIClient()
        client.force_authenticate(user=user_sector_a)
        
        response = client.get(f'/api/cameras/{camera_sector_b.id}/')
        
        assert response.status_code == 403

    def test_user_cannot_update_other_sector_camera(self, user_sector_a, camera_sector_b):
        """Usuário do Setor A não pode atualizar câmera do Setor B"""
        client = APIClient()
        client.force_authenticate(user=user_sector_a)
        
        response = client.patch(f'/api/cameras/{camera_sector_b.id}/', {'name': 'Hack'})
        
        assert response.status_code == 403

    def test_user_cannot_delete_other_sector_camera(self, user_sector_a, camera_sector_b):
        """Usuário do Setor A não pode deletar câmera do Setor B"""
        client = APIClient()
        client.force_authenticate(user=user_sector_a)
        
        response = client.delete(f'/api/cameras/{camera_sector_b.id}/')
        
        assert response.status_code == 403
        assert Camera.objects.filter(id=camera_sector_b.id).exists()

    def test_user_can_access_own_sector_camera(self, user_sector_a, camera_sector_a):
        """Usuário do Setor A pode acessar câmera do próprio setor"""
        client = APIClient()
        client.force_authenticate(user=user_sector_a)
        
        response = client.get(f'/api/cameras/{camera_sector_a.id}/')
        
        assert response.status_code == 200
        assert response.data['id'] == camera_sector_a.id

    def test_unauthenticated_cannot_access(self, camera_sector_a):
        """Usuário não autenticado não pode acessar câmeras"""
        client = APIClient()
        response = client.get('/api/cameras/')
        assert response.status_code == 401

    def test_user_with_multiple_sectors(self, user_sector_a, sector_b, camera_sector_a, camera_sector_b):
        """Usuário com múltiplos setores vê todas as câmeras"""
        user_sector_a.sectors.add(sector_b)
        
        client = APIClient()
        client.force_authenticate(user=user_sector_a)
        
        response = client.get('/api/cameras/')
        
        assert response.status_code == 200
        camera_ids = [cam['id'] for cam in response.data.get('results', response.data)]
        assert camera_sector_a.id in camera_ids
        assert camera_sector_b.id in camera_ids
