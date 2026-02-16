from django.core.management.base import BaseCommand
from apps.iam.models import IAMPermission

class Command(BaseCommand):
    help = 'Carrega permissões iniciais do sistema'

    def handle(self, *args, **options):
        permissions = [
            {'code': 'cameras.view', 'name': 'Visualizar Câmeras', 'description': 'Permite visualizar lista e streams de câmeras', 'resource': 'cameras'},
            {'code': 'cameras.create', 'name': 'Criar Câmeras', 'description': 'Permite adicionar novas câmeras ao sistema', 'resource': 'cameras'},
            {'code': 'cameras.edit', 'name': 'Editar Câmeras', 'description': 'Permite modificar configurações de câmeras existentes', 'resource': 'cameras'},
            {'code': 'cameras.delete', 'name': 'Deletar Câmeras', 'description': 'Permite remover câmeras do sistema', 'resource': 'cameras'},
            {'code': 'recordings.view', 'name': 'Visualizar Gravações', 'description': 'Permite acessar e visualizar gravações', 'resource': 'recordings'},
            {'code': 'recordings.download', 'name': 'Baixar Gravações', 'description': 'Permite fazer download de arquivos de gravação', 'resource': 'recordings'},
            {'code': 'recordings.delete', 'name': 'Deletar Gravações', 'description': 'Permite remover gravações do sistema', 'resource': 'recordings'},
            {'code': 'detections.view', 'name': 'Visualizar Detecções', 'description': 'Permite visualizar detecções de LPR e eventos', 'resource': 'detections'},
            {'code': 'users.manage', 'name': 'Gerenciar Usuários', 'description': 'Permite criar, editar e deletar usuários', 'resource': 'users'},
            {'code': 'settings.manage', 'name': 'Gerenciar Configurações', 'description': 'Permite alterar configurações do sistema', 'resource': 'settings'},
        ]

        created = 0
        for perm_data in permissions:
            perm, created_flag = IAMPermission.objects.get_or_create(
                code=perm_data['code'],
                defaults=perm_data
            )
            if created_flag:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Criada: {perm.code}'))
            else:
                self.stdout.write(f'  Já existe: {perm.code}')

        self.stdout.write(self.style.SUCCESS(f'\n{created} permissões criadas, {len(permissions) - created} já existiam'))
