from django.core.management.base import BaseCommand
from apps.tenants.models import Organization, Subscription
from apps.usuarios.models import Usuario

class Command(BaseCommand):
    help = 'Popula dados de teste para multi-tenant'

    def handle(self, *args, **kwargs):
        # Criar organizações
        org1, _ = Organization.objects.get_or_create(
            slug='sao-paulo',
            defaults={
                'name': 'São Paulo',
                'database_name': 'vms_sao_paulo',
                'is_active': True
            }
        )
        
        org2, _ = Organization.objects.get_or_create(
            slug='rio-janeiro',
            defaults={
                'name': 'Rio de Janeiro',
                'database_name': 'vms_rio_janeiro',
                'is_active': True
            }
        )
        
        # Criar subscriptions
        sub1, _ = Subscription.objects.get_or_create(
            organization=org1,
            defaults={'plan': 'pro', 'is_active': True}
        )
        
        sub2, _ = Subscription.objects.get_or_create(
            organization=org2,
            defaults={'plan': 'basic', 'is_active': True}
        )
        
        # Criar usuários
        user1, created1 = Usuario.objects.get_or_create(
            email='admin@saopaulo.com',
            defaults={
                'name': 'Admin SP',
                'role': 'admin',
                'organization': org1
            }
        )
        if created1:
            user1.set_password('senha123')
            user1.save()
        
        user2, created2 = Usuario.objects.get_or_create(
            email='admin@rio.com',
            defaults={
                'name': 'Admin RJ',
                'role': 'admin',
                'organization': org2
            }
        )
        if created2:
            user2.set_password('senha123')
            user2.save()
        
        self.stdout.write(self.style.SUCCESS('✅ Dados de teste criados!'))
        self.stdout.write(f'Org 1: {org1.name} - Plano: {sub1.plan} ({sub1.recording_days} dias)')
        self.stdout.write(f'Org 2: {org2.name} - Plano: {sub2.plan} ({sub2.recording_days} dias)')
