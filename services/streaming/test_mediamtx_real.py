#!/usr/bin/env python3
"""
Teste direto do MediaMTX com câmeras reais
Execute: docker-compose exec streaming python /app/test_mediamtx_real.py
"""
import httpx
import os
import time

# Configuração
MEDIAMTX_URL = os.getenv("MEDIAMTX_API_URL", "http://mediamtx:9997")
MEDIAMTX_USER = os.getenv("MEDIAMTX_API_USER", "mediamtx_api_user")
MEDIAMTX_PASS = os.getenv("MEDIAMTX_API_PASS", "GtV!sionMed1aMTX$2025")

# Câmeras para teste
TEST_CAMERAS = [
    ("test_intelbras_1", "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0"),
    ("test_intelbras_2", "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0"),
    ("test_rtmp_1", "rtmp://inst-iwvio-srs-rtmp-intelbras.camerite.services:1935/record/7KOM27157189T.stream"),
    ("test_hikvision_1", "rtsp://admin:Camerite@186.226.193.111:602/h264/ch1/main/av_stream"),
]

def add_path(name: str, source: str) -> bool:
    """Adiciona path no MediaMTX"""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{MEDIAMTX_URL}/v3/config/paths/add/{name}",
                json={"source": source, "sourceOnDemand": True},
                auth=(MEDIAMTX_USER, MEDIAMTX_PASS)
            )
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"    ❌ Erro: {e}")
        return False

def get_path(name: str):
    """Obtém informações do path"""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(
                f"{MEDIAMTX_URL}/v3/config/paths/get/{name}",
                auth=(MEDIAMTX_USER, MEDIAMTX_PASS)
            )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def delete_path(name: str) -> bool:
    """Remove path do MediaMTX"""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.delete(
                f"{MEDIAMTX_URL}/v3/config/paths/delete/{name}",
                auth=(MEDIAMTX_USER, MEDIAMTX_PASS)
            )
        return response.status_code in [200, 204, 404]
    except:
        return False

def main():
    print("=" * 70)
    print("🎥 TESTE DIRETO DO MEDIAMTX COM CÂMERAS REAIS")
    print("=" * 70)
    print(f"URL: {MEDIAMTX_URL}")
    print(f"User: {MEDIAMTX_USER}")
    print()
    
    added_paths = []
    
    # Adiciona paths
    print(f"1️⃣ Adicionando {len(TEST_CAMERAS)} câmeras no MediaMTX...")
    for name, source in TEST_CAMERAS:
        print(f"\n  📹 {name}")
        print(f"     {source[:60]}...")
        
        if add_path(name, source):
            print(f"     ✅ Adicionado com sucesso")
            added_paths.append(name)
        else:
            print(f"     ❌ Falha ao adicionar")
        
        time.sleep(0.3)
    
    print()
    print(f"✅ {len(added_paths)}/{len(TEST_CAMERAS)} câmeras adicionadas")
    print()
    
    # Verifica paths
    if added_paths:
        print("2️⃣ Verificando configuração...")
        for name in added_paths[:2]:  # Verifica apenas as 2 primeiras
            info = get_path(name)
            if info:
                source = info.get("source", "N/A")
                on_demand = info.get("sourceOnDemand", False)
                print(f"  ✅ {name}: on_demand={on_demand}")
            else:
                print(f"  ⚠️ {name}: não encontrado")
        print()
    
    # URLs de acesso
    if added_paths:
        print("3️⃣ URLs de acesso (HLS):")
        for name in added_paths:
            print(f"  🔗 http://localhost:8888/{name}/")
        print()
    
    # Limpeza
    print("4️⃣ Removendo paths de teste...")
    for name in added_paths:
        if delete_path(name):
            print(f"  ✅ {name} removido")
        else:
            print(f"  ⚠️ {name} falha ao remover")
    
    print()
    print("=" * 70)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 70)

if __name__ == "__main__":
    main()
