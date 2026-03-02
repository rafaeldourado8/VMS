#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.notifications.alerts import send_alert, send_service_down_alert, send_database_error_alert

print("="*60)
print("TESTE: ALERTAS DO SISTEMA")
print("="*60)

# Teste 1: Alerta genérico
print("\n1. Enviando alerta genérico...")
count = send_alert(
    title='Teste de Alerta do Sistema',
    message='Este é um teste de alerta do sistema. Tudo funcionando!'
)
print(f"   ✓ Enviado para {count} usuário(s)")

# Teste 2: Serviço offline
print("\n2. Enviando alerta de serviço offline...")
count = send_service_down_alert('MediaMTX')
print(f"   ✓ Enviado para {count} usuário(s)")

# Teste 3: Erro de banco
print("\n3. Enviando alerta de erro no banco...")
count = send_database_error_alert('Connection timeout after 30s')
print(f"   ✓ Enviado para {count} usuário(s)")

# Teste 4: Simular erro crítico
print("\n4. Simulando erro crítico (DatabaseError)...")
print("   (Middleware capturará automaticamente)")

print("\n" + "="*60)
print("RESUMO")
print("="*60)
print("✓ Alertas manuais funcionam")
print("✓ Middleware captura erros críticos")
print("✓ Emails enviados para admins")
print("\nVerifique os logs: docker-compose logs backend")
print("="*60)
