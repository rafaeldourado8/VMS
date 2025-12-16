"""
Testes de Integridade e Persistência do Banco de Dados
"""
import pytest
from django.db import transaction, IntegrityError
from apps.cameras.models import Camera
from apps.deteccoes.models import Deteccao


@pytest.mark.django_db
class TestDatabaseIntegrity:
    """Testes de integridade do banco de dados"""

    def test_camera_unique_constraint(self, test_user):
        """Teste constraint de unicidade"""
        Camera.objects.create(
            nome='Unique Camera',
            rtsp_url='rtsp://test@192.168.1.1:554/stream',
            localizacao='Test',
            ativa=True,
            criado_por=test_user
        )
        
        # Tentar criar câmera duplicada deve falhar
        with pytest.raises(IntegrityError):
            Camera.objects.create(
                nome='Unique Camera',
                rtsp_url='rtsp://test@192.168.1.1:554/stream',
                localizacao='Test',
                ativa=True,
                criado_por=test_user
            )

    def test_foreign_key_constraint(self, test_camera):
        """Teste constraint de chave estrangeira"""
        # Criar detecção
        deteccao = Deteccao.objects.create(
            camera=test_camera,
            tipo_objeto='pessoa',
            confianca=0.95,
            bbox_x=100,
            bbox_y=100,
            bbox_width=200,
            bbox_height=300
        )
        
        # Deletar câmera deve deletar detecções (CASCADE)
        camera_id = test_camera.id
        test_camera.delete()
        
        assert not Deteccao.objects.filter(camera_id=camera_id).exists()

    def test_transaction_rollback(self, test_user):
        """Teste rollback de transação"""
        initial_count = Camera.objects.count()
        
        try:
            with transaction.atomic():
                Camera.objects.create(
                    nome='Transaction Test',
                    rtsp_url='rtsp://test@192.168.1.1:554/stream',
                    localizacao='Test',
                    ativa=True,
                    criado_por=test_user
                )
                # Forçar erro
                raise Exception("Rollback test")
        except Exception:
            pass
        
        # Contagem deve ser a mesma (rollback)
        assert Camera.objects.count() == initial_count

    def test_data_persistence_after_update(self, test_camera):
        """Teste persistência após atualização"""
        original_name = test_camera.nome
        test_camera.nome = 'Updated Name'
        test_camera.save()
        
        # Recarregar do banco
        test_camera.refresh_from_db()
        assert test_camera.nome == 'Updated Name'
        assert test_camera.nome != original_name

    def test_cascade_delete(self, test_user):
        """Teste deleção em cascata"""
        camera = Camera.objects.create(
            nome='Cascade Test',
            rtsp_url='rtsp://test@192.168.1.1:554/stream',
            localizacao='Test',
            ativa=True,
            criado_por=test_user
        )
        
        # Criar múltiplas detecções
        for i in range(10):
            Deteccao.objects.create(
                camera=camera,
                tipo_objeto='pessoa',
                confianca=0.9,
                bbox_x=i*10,
                bbox_y=i*10,
                bbox_width=100,
                bbox_height=100
            )
        
        camera_id = camera.id
        camera.delete()
        
        # Todas detecções devem ser deletadas
        assert Deteccao.objects.filter(camera_id=camera_id).count() == 0


@pytest.mark.django_db
class TestDataValidation:
    """Testes de validação de dados"""

    def test_required_fields(self, test_user):
        """Teste campos obrigatórios"""
        with pytest.raises(IntegrityError):
            Camera.objects.create(
                nome='Test',
                # rtsp_url faltando (obrigatório)
                localizacao='Test',
                ativa=True,
                criado_por=test_user
            )

    def test_field_max_length(self, test_user):
        """Teste tamanho máximo de campos"""
        long_name = 'A' * 300  # Exceder max_length
        
        camera = Camera(
            nome=long_name,
            rtsp_url='rtsp://test@192.168.1.1:554/stream',
            localizacao='Test',
            ativa=True,
            criado_por=test_user
        )
        
        # Validação deve falhar
        with pytest.raises(Exception):
            camera.full_clean()

    def test_confidence_range_validation(self, test_camera):
        """Teste validação de range de confiança"""
        # Confiança deve estar entre 0 e 1
        with pytest.raises(Exception):
            Deteccao.objects.create(
                camera=test_camera,
                tipo_objeto='pessoa',
                confianca=1.5,  # Inválido
                bbox_x=100,
                bbox_y=100,
                bbox_width=200,
                bbox_height=300
            )


@pytest.mark.django_db
class TestConcurrency:
    """Testes de concorrência"""

    def test_concurrent_updates(self, test_camera):
        """Teste atualizações concorrentes"""
        from django.db import connection
        from threading import Thread
        
        def update_camera(name):
            camera = Camera.objects.get(id=test_camera.id)
            camera.nome = name
            camera.save()
        
        # Simular atualizações concorrentes
        thread1 = Thread(target=update_camera, args=('Name1',))
        thread2 = Thread(target=update_camera, args=('Name2',))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Verificar que última atualização prevaleceu
        test_camera.refresh_from_db()
        assert test_camera.nome in ['Name1', 'Name2']
