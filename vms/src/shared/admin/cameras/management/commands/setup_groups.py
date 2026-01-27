from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from shared.admin.cameras.models import Camera

class Command(BaseCommand):
    help = 'Cria grupos de permissões padrão (GESTOR e USER)'

    def handle(self, *args, **options):
        camera_ct = ContentType.objects.get_for_model(Camera)
        
        view_camera = Permission.objects.get(codename='view_camera', content_type=camera_ct)
        add_camera = Permission.objects.get(codename='add_camera', content_type=camera_ct)
        change_camera = Permission.objects.get(codename='change_camera', content_type=camera_ct)
        delete_camera = Permission.objects.get(codename='delete_camera', content_type=camera_ct)
        view_city_cameras = Permission.objects.get(codename='view_city_cameras', content_type=camera_ct)
        manage_city_cameras = Permission.objects.get(codename='manage_city_cameras', content_type=camera_ct)
        
        gestor_group, created = Group.objects.get_or_create(name='GESTOR')
        gestor_group.permissions.set([
            view_camera,
            add_camera,
            change_camera,
            delete_camera,
            manage_city_cameras,
            view_city_cameras,
        ])
        self.stdout.write(self.style.SUCCESS(f'✓ Grupo GESTOR {"criado" if created else "atualizado"}'))
        
        user_group, created = Group.objects.get_or_create(name='USER')
        user_group.permissions.set([
            view_camera,
            view_city_cameras,
        ])
        self.stdout.write(self.style.SUCCESS(f'✓ Grupo USER {"criado" if created else "atualizado"}'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Grupos configurados'))
