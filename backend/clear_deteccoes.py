import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.deteccoes.models import Deteccao

Deteccao.objects.all().delete()
print('✅ Detecções antigas removidas')
