#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.notifications.models import NotificationPreference
from apps.usuarios.models import Usuario

print("="*60)
print("STATUS DAS NOTIFICAÇÕES")
print("="*60)

# 1. Verificar se preferências funcionam
print("\n1. Preferências de Notificação:")
user = Usuario.objects.first()
if user:
    prefs, created = NotificationPreference.objects.get_or_create(user=user)
    print(f"   ✓ Modelo funciona: {'Criado' if created else 'Já existe'}")
    print(f"   - Email alerts: {prefs.email_alerts}")
    print(f"   - Detection alerts: {prefs.detection_alerts}")
    print(f"   - Camera offline: {prefs.camera_offline}")
else:
    print("   ✗ Nenhum usuário encontrado")

# 2. Verificar API
print("\n2. API REST:")
print("   ✓ GET /api/notifications/preferences/ - Implementado")
print("   ✓ PATCH /api/notifications/preferences/ - Implementado")
print("   ✓ Frontend atualiza via React Query")

# 3. Verificar funcionalidades reais
print("\n3. Funcionalidades Implementadas:")
print("   ✓ Login Log - Email enviado quando alguém loga")
print("   ❌ Alertas de Detecção LPR - NÃO implementado")
print("   ❌ Câmera Offline - NÃO implementado")
print("   ❌ Alertas do Sistema - NÃO implementado")
print("   ❌ Aviso de Armazenamento - NÃO implementado")
print("   ❌ Relatório Diário - NÃO implementado")

# 4. O que precisa ser feito
print("\n4. Para Implementar:")
print("   - Criar signals para câmera offline")
print("   - Criar task Celery para relatório diário")
print("   - Criar monitor de armazenamento")
print("   - Integrar com detecções LPR")

print("\n" + "="*60)
print("CONCLUSÃO: Apenas Login Log funciona de verdade")
print("="*60)
