"""
Comando para reprovisionar todas as câmeras no MediaMTX
"""
from django.core.management.base import BaseCommand
from apps.cameras.services import CameraService


class Command(BaseCommand):
    help = 'Reprovisiona todas as câmeras no MediaMTX via Streaming Service'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Iniciando reprovisionamento de câmeras...')
        
        service = CameraService()
        results = service.reprovision_all_cameras()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Reprovisionamento concluído: '
                f'{results["success"]}/{results["total"]} câmeras OK, '
                f'{results["failed"]} falhas'
            )
        )
