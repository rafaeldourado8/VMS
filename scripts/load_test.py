#!/usr/bin/env python3
"""Teste de carga - 10 câmeras simultâneas."""

import asyncio
import httpx
import time
import psutil
import json
from datetime import datetime

STREAMING_API = "http://localhost:8001"
MEDIAMTX_API = "http://localhost:9997"
AUTH = ("mediamtx_api_user", "GtV!sionMed1aMTX$2025")

# Câmeras de teste
CAMERAS = [
    {"id": 10, "url": "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0"},
    {"id": 11, "url": "rtsp://admin:Camerite123@45.236.226.72:6048/cam/realmonitor?channel=1&subtype=0"},
    {"id": 12, "url": "rtsp://admin:Camerite123@45.236.226.71:6047/cam/realmonitor?channel=1&subtype=0"},
    {"id": 13, "url": "rtsp://admin:Camerite123@45.236.226.70:6045/cam/realmonitor?channel=1&subtype=0"},
    {"id": 14, "url": "rtsp://admin:Camerite123@45.236.226.70:6044/cam/realmonitor?channel=1&subtype=0"},
    {"id": 20, "url": "rtsp://admin:Camerite@186.226.193.111:602/h264/ch1/main/av_stream"},
    {"id": 21, "url": "rtsp://admin:Camerite@186.226.193.111:601/h264/ch1/main/av_stream"},
    {"id": 22, "url": "rtsp://admin:Camerite@186.226.193.111:600/h264/ch1/main/av_stream"},
    {"id": 23, "url": "rtsp://admin:Camerite@170.84.217.84:603/h264/ch1/main/av_stream"},
    {"id": 24, "url": "rtsp://admin:Camerite@170.84.217.83:608/h264/ch1/main/av_stream"},
]

async def provision_camera(client, cam):
    """Provisiona uma câmera."""
    try:
        resp = await client.post(
            f"{STREAMING_API}/cameras/provision",
            json={
                "camera_id": cam["id"],
                "rtsp_url": cam["url"],
                "name": f"Test Camera {cam['id']}",
                "enabled": True,
                "on_demand": False
            },
            timeout=30.0
        )
        result = resp.json()
        return cam["id"], result.get("success", False), result.get("message", "")
    except Exception as e:
        return cam["id"], False, str(e)

async def get_mediamtx_stats(client):
    """Obtém estatísticas do MediaMTX."""
    try:
        resp = await client.get(f"{MEDIAMTX_API}/v3/paths/list", auth=AUTH)
        paths = resp.json().get("items", [])
        
        total_bytes_received = sum(p.get("bytesReceived", 0) for p in paths)
        total_bytes_sent = sum(p.get("bytesSent", 0) for p in paths)
        ready_count = sum(1 for p in paths if p.get("ready"))
        
        return {
            "total_paths": len(paths),
            "ready_paths": ready_count,
            "bytes_received": total_bytes_received,
            "bytes_sent": total_bytes_sent
        }
    except:
        return None

def get_system_stats():
    """Obtém estatísticas do sistema."""
    try:
        import docker
        client = docker.from_env()
        container = client.containers.get("gtvision_mediamtx")
        stats = container.stats(stream=False)
        
        cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
        system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
        cpu_percent = (cpu_delta / system_delta) * len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"]) * 100
        
        mem_usage = stats["memory_stats"]["usage"] / (1024**2)  # MB
        mem_limit = stats["memory_stats"]["limit"] / (1024**2)  # MB
        
        return {
            "cpu_percent": round(cpu_percent, 2),
            "mem_usage_mb": round(mem_usage, 2),
            "mem_limit_mb": round(mem_limit, 2),
            "mem_percent": round((mem_usage / mem_limit) * 100, 2)
        }
    except:
        return None

async def run_load_test():
    """Executa teste de carga."""
    print("="*70)
    print("TESTE DE CARGA - 10 CAMERAS SIMULTANEAS")
    print("="*70)
    
    results = {
        "start_time": datetime.now().isoformat(),
        "cameras": [],
        "stats_timeline": []
    }
    
    async with httpx.AsyncClient() as client:
        # Fase 1: Provisionamento simultâneo
        print("\n[FASE 1] Provisionando 10 cameras simultaneamente...")
        start = time.time()
        
        tasks = [provision_camera(client, cam) for cam in CAMERAS]
        provision_results = await asyncio.gather(*tasks)
        
        provision_time = time.time() - start
        
        success_count = sum(1 for _, success, _ in provision_results if success)
        print(f"\nResultado: {success_count}/{len(CAMERAS)} cameras provisionadas")
        print(f"Tempo total: {provision_time:.2f}s")
        print(f"Tempo medio por camera: {provision_time/len(CAMERAS):.2f}s")
        
        for cam_id, success, msg in provision_results:
            status = "OK" if success else "FALHOU"
            print(f"  cam_{cam_id}: {status} - {msg}")
            results["cameras"].append({
                "camera_id": cam_id,
                "success": success,
                "message": msg
            })
        
        # Fase 2: Monitoramento por 5 minutos
        print("\n[FASE 2] Monitorando recursos por 5 minutos...")
        print(f"{'Tempo':<10} {'CPU%':<8} {'RAM MB':<10} {'Paths':<8} {'RX MB':<12} {'TX MB':<12}")
        print("-"*70)
        
        for i in range(60):  # 5 minutos (5s interval)
            mediamtx_stats = await get_mediamtx_stats(client)
            system_stats = get_system_stats()
            
            if mediamtx_stats and system_stats:
                rx_mb = mediamtx_stats["bytes_received"] / (1024**2)
                tx_mb = mediamtx_stats["bytes_sent"] / (1024**2)
                
                print(f"{i*5:<10} {system_stats['cpu_percent']:<8} "
                      f"{system_stats['mem_usage_mb']:<10} "
                      f"{mediamtx_stats['ready_paths']:<8} "
                      f"{rx_mb:<12.2f} {tx_mb:<12.2f}")
                
                results["stats_timeline"].append({
                    "timestamp": datetime.now().isoformat(),
                    "mediamtx": mediamtx_stats,
                    "system": system_stats
                })
            
            await asyncio.sleep(5)
        
        # Fase 3: Estatísticas finais
        print("\n[FASE 3] Estatisticas finais...")
        final_stats = await get_mediamtx_stats(client)
        final_system = get_system_stats()
        
        if final_stats and final_system:
            print(f"\nMediaMTX:")
            print(f"  Paths ativos: {final_stats['ready_paths']}/{final_stats['total_paths']}")
            print(f"  Dados recebidos: {final_stats['bytes_received']/(1024**3):.2f} GB")
            print(f"  Dados enviados: {final_stats['bytes_sent']/(1024**2):.2f} MB")
            
            print(f"\nSistema:")
            print(f"  CPU: {final_system['cpu_percent']}%")
            print(f"  RAM: {final_system['mem_usage_mb']:.0f}/{final_system['mem_limit_mb']:.0f} MB ({final_system['mem_percent']}%)")
        
        results["end_time"] = datetime.now().isoformat()
        results["final_stats"] = {
            "mediamtx": final_stats,
            "system": final_system
        }
    
    # Salvar resultados
    with open("load_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*70)
    print("Resultados salvos em: load_test_results.json")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(run_load_test())
