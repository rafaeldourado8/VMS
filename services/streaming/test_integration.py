import httpx
import asyncio
import sys

# Configurações do ambiente de teste
BASE_URL = "http://localhost:8001" # Porta do Streaming Service
# Usando um stream de teste público se não houver câmera real disponível
TEST_RTSP = "rtsp://rtsp.stream/pattern" 
TEST_CAM_ID = 999

async def run_integration_test():
    print(f"🚀 Iniciando teste de integração: GT-Vision Streaming")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Testar Health Check
        print("🔍 Verificando saúde dos serviços...")
        health = await client.get(f"{BASE_URL}/health")
        if health.status_code != 200:
            print("❌ Erro: Serviço de Streaming ou MediaMTX offline.")
            return
        print(f"✅ Status: {health.json()['status']}")

        # 2. Simular Frontend: Provisionar Câmera
        print(f"🎥 Provisionando câmera {TEST_CAM_ID}...")
        payload = {
            "camera_id": TEST_CAM_ID,
            "name": "Camera de Teste Real",
            "rtsp_url": TEST_RTSP,
            "on_demand": True
        }
        resp = await client.post(f"{BASE_URL}/cameras/provision", json=payload)
        
        if resp.status_code != 200 or not resp.json().get("success"):
            print(f"❌ Falha no provisionamento: {resp.text}")
            return
        
        stream_path = resp.json()["stream_path"]
        print(f"✅ Path criado no MediaMTX: {stream_path}")

        # 3. Aguardar o MediaMTX processar a fonte (On-Demand)
        print("⏳ Aguardando ativação do stream (5s)...")
        await asyncio.sleep(5)

        # 4. Validar se o HLS está sendo servido via Proxy
        print(f"📡 Testando Proxy HLS para {stream_path}...")
        hls_resp = await client.get(f"{BASE_URL}/hls/{stream_path}/index.m3u8")
        
        if hls_resp.status_code == 200:
            print("✅ Playlist HLS (.m3u8) obtida com sucesso via Proxy!")
            if "#EXTM3U" in hls_resp.text:
                print("💎 Conteúdo da playlist validado.")
        else:
            print(f"❌ Erro ao obter HLS: Status {hls_resp.status_code}")

        # 5. Limpeza (Remover câmera)
        print(f"🧹 Removendo câmera de teste...")
        del_resp = await client.delete(f"{BASE_URL}/cameras/{TEST_CAM_ID}")
        if del_resp.status_code == 200:
            print("✅ Câmera removida e path limpo.")

if __name__ == "__main__":
    try:
        asyncio.run(run_integration_test())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"🚨 Erro fatal no teste: {e}")