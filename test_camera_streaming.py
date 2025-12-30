#!/usr/bin/env python3
"""
Script de teste para verificar o streaming de câmeras
Testa o fluxo completo: provisionamento -> HLS -> verificação
"""

import asyncio
import httpx
import time
from typing import Dict, Any

# Configurações
STREAMING_SERVICE_URL = "http://localhost:8001"
MEDIAMTX_HLS_URL = "http://localhost:8888"
HAPROXY_URL = "http://localhost:80"

async def test_camera_provisioning():
    """Testa o provisionamento de uma câmera de teste"""
    
    print("🧪 Testando provisionamento de câmera...")
    
    # Dados de teste
    test_camera = {
        "camera_id": 999,
        "rtsp_url": "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4",
        "name": "Câmera Teste",
        "on_demand": True
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 1. Provisionar câmera
            print(f"📹 Provisionando câmera {test_camera['camera_id']}...")
            response = await client.post(
                f"{STREAMING_SERVICE_URL}/cameras/provision",
                json=test_camera
            )
            
            if response.status_code != 200:
                print(f"❌ Erro no provisionamento: {response.status_code} - {response.text}")
                return False
            
            data = response.json()
            if not data.get("success"):
                print(f"❌ Provisionamento falhou: {data.get('message')}")
                return False
            
            print(f"✅ Câmera provisionada: {data['stream_path']}")
            print(f"   HLS URL: {data['hls_url']}")
            
            # 2. Aguardar um pouco para o MediaMTX processar
            print("⏳ Aguardando MediaMTX processar...")
            await asyncio.sleep(3)
            
            # 3. Testar acesso direto ao MediaMTX
            hls_path = f"cam_{test_camera['camera_id']}/index.m3u8"
            print(f"🔍 Testando acesso direto ao MediaMTX: {hls_path}")
            
            response = await client.get(f"{MEDIAMTX_HLS_URL}/{hls_path}")
            print(f"   MediaMTX direto: {response.status_code}")
            
            # 4. Testar via HAProxy
            print(f"🔍 Testando via HAProxy: /hls/{hls_path}")
            response = await client.get(f"{HAPROXY_URL}/hls/{hls_path}")
            print(f"   HAProxy: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ HLS funcionando via HAProxy!")
                # Mostrar primeiras linhas do playlist
                content = response.text
                lines = content.split('\n')[:5]
                print("   Playlist preview:")
                for line in lines:
                    if line.strip():
                        print(f"     {line}")
            else:
                print(f"❌ HLS não funcionando via HAProxy: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
            
            # 5. Verificar status da câmera
            print(f"📊 Verificando status da câmera...")
            response = await client.get(f"{STREAMING_SERVICE_URL}/cameras/{test_camera['camera_id']}/status")
            if response.status_code == 200:
                status = response.json()
                print(f"   Status: {status.get('status')}")
                print(f"   Viewers: {status.get('viewers', 0)}")
            
            # 6. Limpar - remover câmera de teste
            print(f"🗑️ Removendo câmera de teste...")
            await client.delete(f"{STREAMING_SERVICE_URL}/cameras/{test_camera['camera_id']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro durante teste: {str(e)}")
            return False

async def test_streaming_stats():
    """Testa as estatísticas do streaming service"""
    print("\n📊 Testando estatísticas do streaming...")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{STREAMING_SERVICE_URL}/stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Stats obtidas:")
                print(f"   Streams ativos: {stats.get('active_streams', 0)}")
                print(f"   Total viewers: {stats.get('total_viewers', 0)}")
                print(f"   Uptime: {stats.get('uptime_seconds', 0):.1f}s")
                return True
            else:
                print(f"❌ Erro ao obter stats: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return False

async def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes de streaming de câmeras\n")
    
    # Teste 1: Stats
    stats_ok = await test_streaming_stats()
    
    # Teste 2: Provisionamento completo
    provision_ok = await test_camera_provisioning()
    
    print(f"\n📋 Resumo dos testes:")
    print(f"   Stats: {'✅' if stats_ok else '❌'}")
    print(f"   Provisionamento: {'✅' if provision_ok else '❌'}")
    
    if stats_ok and provision_ok:
        print("\n🎉 Todos os testes passaram! O streaming está funcionando.")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    asyncio.run(main())