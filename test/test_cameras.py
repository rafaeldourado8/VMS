import httpx
import asyncio
import os
import sys

# Pega a URL do ambiente (Docker) ou usa localhost (Manual)
STREAMING_URL = os.environ.get("STREAMING_API_URL", "http://localhost:8001")

CAMERAS = [
    {"id": 101, "name": "Entrada 75-6053", "url": "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0"},
    {"id": 102, "name": "Entrada 75-6052", "url": "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0"},
    {"id": 103, "name": "Rua 74-6050", "url": "rtsp://admin:Camerite123@45.236.226.74:6050/cam/realmonitor?channel=1&subtype=0"},
    {"id": 104, "name": "Rua 72-6049", "url": "rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0"},
]

async def test_real_cameras():
    print(f"🚀 Conectando ao Streaming Service em: {STREAMING_URL}")
    
    async with httpx.AsyncClient(timeout=40.0) as client:
        # 1. Provisionar Câmeras
        for cam in CAMERAS:
            print(f"🎬 Provisionando: {cam['name']}...")
            payload = {
                "camera_id": cam['id'],
                "rtsp_url": cam['url'],
                "name": cam['name'],
                "on_demand": False # Força o MediaMTX/FFmpeg a conectar agora
            }
            try:
                resp = await client.post(f"{STREAMING_URL}/cameras/provision", json=payload)
                if resp.status_code == 200:
                    print(f"   ✅ cam_{cam['id']} Criada.")
            except Exception as e:
                print(f"   ❌ Erro ao conectar: {e}")
                return

        # 2. Aguardar o processamento do FFmpeg
        print("\n⏳ Aguardando 15s para FFmpeg estabilizar os streams e iniciar gravações...")
        await asyncio.sleep(15)

        # 3. Validar HLS e Gravações
        print("\n📡 Validando Proxy HLS e Fragmentos de Vídeo...")
        for cam in CAMERAS:
            path = f"cam_{cam['id']}"
            hls_url = f"{STREAMING_URL}/hls/{path}/index.m3u8"
            
            try:
                resp = await client.get(hls_url)
                if resp.status_code == 200 and "#EXTM3U" in resp.text:
                    status = "OK (HLS Ativo)"
                    # Verifica se o FFmpeg já gerou segmentos reais
                    if ".m4s" in resp.text or ".ts" in resp.text:
                        status += " + FFmpeg Gravando 📹"
                    print(f"💎 {path}: {status}")
                else:
                    print(f"⚠️ {path}: Sem sinal (Status {resp.status_code})")
            except:
                print(f"❌ {path}: Erro de rede")

        # 4. Estatísticas Finais
        stats = await client.get(f"{STREAMING_URL}/stats")
        if stats.status_code == 200:
            s = stats.json()
            print(f"\n📊 Resumo: {s['active_streams']} câmeras online | {s['total_bytes_sent']} bytes trafegados.")

if __name__ == "__main__":
    asyncio.run(test_real_cameras())