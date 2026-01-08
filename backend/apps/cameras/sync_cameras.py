"""
GT-Vision - Comando de Sincronização de Câmeras
================================================
Uso: python manage.py sync_cameras

Este comando provisiona todas as câmeras existentes no banco de dados
no MediaMTX. Útil para:
- Inicialização do sistema
- Após restart do MediaMTX
- Recuperação de estado
"""

from django.core.management.base import BaseCommand, CommandError
from apps.cameras.models import Camera
from apps.cameras.services import CameraService

class Command(BaseCommand):
    help = 'Sincroniza todas as câmeras do banco de dados com o MediaMTX'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Email do usuário para sincronizar apenas suas câmeras',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem executar',
        )

    def handle(self, *args, **options):
        service = CameraService()
        
        # Filtrar por usuário se especificado
        if options['user']:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(email=options['user'])
                cameras = Camera.objects.filter(owner=user)
                self.stdout.write(f"Sincronizando câmeras do usuário: {user.email}")
            except User.DoesNotExist:
                raise CommandError(f"Usuário '{options['user']}' não encontrado")
        else:
            cameras = Camera.objects.all()
            self.stdout.write("Sincronizando TODAS as câmeras do sistema")

        total = cameras.count()
        self.stdout.write(f"Total de câmeras: {total}")
        self.stdout.write("-" * 50)

        if options['dry_run']:
            self.stdout.write(self.style.WARNING("MODO DRY-RUN - Nenhuma alteração será feita"))
            for camera in cameras:
                self.stdout.write(f"  [DRY] cam_{camera.id}: {camera.name} -> {camera.stream_url[:50]}...")
            return

        success = 0
        failed = 0

        for camera in cameras:
            self.stdout.write(f"  Provisionando cam_{camera.id}: {camera.name}...", ending=" ")
            
            try:
                result = service._provision_streaming(camera)
                if result:
                    self.stdout.write(self.style.SUCCESS("✓"))
                    success += 1
                else:
                    self.stdout.write(self.style.ERROR("✗"))
                    failed += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ ({str(e)})"))
                failed += 1

        self.stdout.write("-" * 50)
        self.stdout.write(
            f"Resultado: {self.style.SUCCESS(f'{success} OK')} | "
            f"{self.style.ERROR(f'{failed} FALHAS')} | "
            f"Total: {total}"
        )

        if failed > 0:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  Algumas câmeras falharam. Verifique:\n"
                    "   1. Se o Streaming Service está rodando\n"
                    "   2. Se o MediaMTX está acessível\n"
                    "   3. Logs do Django e Streaming Service"
                )
            )