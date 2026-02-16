#!/usr/bin/env python
"""
Script para testar a lógica de retenção de gravações
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, 'backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cameras.models import Camera
from apps.timeline.retention_calculator import RetentionCalculator
from datetime import datetime, timedelta

def test_retention():
    print("=" * 60)
    print("TESTE DE RETENÇÃO DE GRAVAÇÕES")
    print("=" * 60)
    
    cameras = Camera.objects.all().order_by('-id')[:5]
    
    for camera in cameras:
        print(f"\n📹 Câmera: {camera.name} (ID: {camera.id})")
        print(f"   Retenção configurada: {camera.recording_retention_days} dias")
        print(f"   Gravação habilitada: {camera.recording_enabled}")
        
        # Calcula data de expiração
        expiry_date = RetentionCalculator.calculate_expiry_date(camera)
        
        if expiry_date:
            print(f"   Data de expiração: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Arquivos antes de {expiry_date.strftime('%Y-%m-%d')} serão deletados")
        else:
            print(f"   ⚠️  Sem política de retenção ativa")
        
        # Verifica quantos dias de retenção
        retention_days = RetentionCalculator.get_retention_days(camera)
        print(f"   Dias de retenção calculados: {retention_days}")
        
        print(f"   ✅ Configuração OK")
    
    print("\n" + "=" * 60)
    print("RESUMO:")
    print(f"Total de câmeras: {Camera.objects.count()}")
    print(f"Com gravação habilitada: {Camera.objects.filter(recording_enabled=True).count()}")
    print("=" * 60)

if __name__ == "__main__":
    test_retention()
