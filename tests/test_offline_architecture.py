"""
Script de Teste - Arquitetura Offline LPR
Valida gravação, indexação e processamento
"""
import asyncio
import httpx
from datetime import datetime, timedelta

async def test_architecture():
    print("=== TESTE DE ARQUITETURA OFFLINE LPR ===\n")
    
    # 1. Verificar MediaMTX
    print("1. Testando MediaMTX...")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get("http://localhost:9997/v3/config/global/get",
                                   auth=("mediamtx_api_user", "GtV!sionMed1aMTX$2025"))
            print(f"   ✓ MediaMTX: {resp.status_code}")
        except Exception as e:
            print(f"   ✗ MediaMTX: {e}")
    
    # 2. Verificar Storage Service
    print("\n2. Testando Storage Service...")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get("http://localhost:8003/health")
            print(f"   ✓ Storage: {resp.status_code}")
            
            # Estatísticas
            resp = await client.get("http://localhost:8003/recordings/stats")
            stats = resp.json()
            print(f"   - Total segmentos: {stats['total_segments']}")
            print(f"   - Processados: {stats['processed_segments']}")
            print(f"   - Pendentes: {stats['pending_segments']}")
            print(f"   - Tamanho total: {stats['total_size_gb']} GB")
        except Exception as e:
            print(f"   ✗ Storage: {e}")
    
    # 3. Testar consulta de gravações
    print("\n3. Testando consulta de gravações...")
    async with httpx.AsyncClient() as client:
        try:
            query = {
                "camera_id": 2,
                "start_time": (datetime.now() - timedelta(hours=2)).isoformat(),
                "end_time": datetime.now().isoformat()
            }
            resp = await client.post("http://localhost:8003/recordings/query", json=query)
            recordings = resp.json()
            print(f"   ✓ Encontradas {len(recordings)} gravações para câmera 2")
            
            if recordings:
                rec = recordings[0]
                print(f"   - Exemplo: {rec['path']}")
                print(f"   - Período: {rec['start_time']} → {rec['end_time']}")
                print(f"   - Processado: {rec['processed']}")
        except Exception as e:
            print(f"   ✗ Consulta: {e}")
    
    # 4. Verificar Streaming Service
    print("\n4. Testando Streaming Service...")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get("http://localhost:8001/health")
            print(f"   ✓ Streaming: {resp.status_code}")
            
            # Stats
            resp = await client.get("http://localhost:8001/stats")
            stats = resp.json()
            print(f"   - Streams ativos: {stats['active_streams']}")
            print(f"   - Viewers: {stats['total_viewers']}")
        except Exception as e:
            print(f"   ✗ Streaming: {e}")
    
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    asyncio.run(test_architecture())
