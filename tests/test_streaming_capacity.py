import asyncio
import aiohttp
import time
import json
from datetime import datetime

# Lista de câmeras para teste
CAMERAS = [
    {"name": "Camera 1", "url": "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0", "location": "Teste 1"},
    {"name": "Camera 2", "url": "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0", "location": "Teste 2"},
    {"name": "Camera 3", "url": "rtsp://admin:Camerite123@45.236.226.74:6050/cam/realmonitor?channel=1&subtype=0", "location": "Teste 3"},
    {"name": "Camera 4", "url": "rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0", "location": "Teste 4"},
    {"name": "Camera 5", "url": "rtsp://admin:Camerite123@45.236.226.72:6048/cam/realmonitor?channel=1&subtype=0", "location": "Teste 5"},
    {"name": "Camera 6", "url": "rtsp://admin:Camerite123@45.236.226.71:6047/cam/realmonitor?channel=1&subtype=0", "location": "Teste 6"},
    {"name": "Camera 7", "url": "rtsp://admin:Camerite123@45.236.226.71:6046/cam/realmonitor?channel=1&subtype=0", "location": "Teste 7"},
    {"name": "Camera 8", "url": "rtsp://admin:Camerite123@45.236.226.70:6045/cam/realmonitor?channel=1&subtype=0", "location": "Teste 8"},
    {"name": "Camera 9", "url": "rtsp://admin:Camerite123@45.236.226.70:6044/cam/realmonitor?channel=1&subtype=0", "location": "Teste 9"},
    {"name": "Camera 10", "url": "rtmp://inst-iwvio-srs-rtmp-intelbras.camerite.services:1935/record/7KOM27157189T.stream", "location": "RTMP 1"},
    {"name": "Camera 11", "url": "rtsp://admin:Camerite@186.226.193.111:602/h264/ch1/main/av_stream", "location": "Teste 11"},
    {"name": "Camera 12", "url": "rtsp://admin:Camerite@186.226.193.111:601/h264/ch1/main/av_stream", "location": "Teste 12"},
    {"name": "Camera 13", "url": "rtsp://admin:Camerite@170.84.217.84:603/h264/ch1/main/av_stream", "location": "Teste 13"},
    {"name": "Camera 14", "url": "rtmp://inst-czd17-srs-rtmp-hik-pro-connect.camerite.services:1935/record/FC2487833.stream", "location": "RTMP 2"},
    {"name": "Camera 15", "url": "rtmp://inst-czd17-srs-rtmp-hik-pro-connect.camerite.services:1935/record/FC2487237.stream", "location": "RTMP 3"},
]

class StreamingTester:
    def __init__(self):
        self.base_url = "http://localhost"
        self.results = []
        
    async def login(self, session):
        """Faz login no sistema"""
        login_data = {
            "email": "admin@test.com",
            "password": "admin123"
        }
        
        async with session.post(f"{self.base_url}/api/auth/login/", json=login_data) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get('access')
            return None
    
    async def create_camera(self, session, token, camera_data):
        """Cria uma câmera via API"""
        headers = {"Authorization": f"Bearer {token}"}
        
        payload = {
            "name": camera_data["name"],
            "stream_url": camera_data["url"],
            "location": camera_data["location"]
        }
        
        start_time = time.time()
        
        try:
            async with session.post(f"{self.base_url}/api/cameras/", 
                                  json=payload, headers=headers) as resp:
                creation_time = time.time() - start_time
                
                if resp.status == 201:
                    data = await resp.json()
                    return {
                        "success": True,
                        "camera_id": data["id"],
                        "creation_time": creation_time,
                        "name": camera_data["name"]
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {resp.status}",
                        "creation_time": creation_time,
                        "name": camera_data["name"]
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "creation_time": time.time() - start_time,
                "name": camera_data["name"]
            }
    
    async def test_hls_stream(self, session, camera_id):
        """Testa latência do stream HLS"""
        hls_url = f"http://localhost:8888/cam_{camera_id}/index.m3u8"
        
        start_time = time.time()
        
        try:
            async with session.get(hls_url) as resp:
                latency = time.time() - start_time
                
                if resp.status == 200:
                    content = await resp.text()
                    segments = content.count('.ts')
                    return {
                        "success": True,
                        "latency": latency,
                        "segments": segments,
                        "status": resp.status
                    }
                else:
                    return {
                        "success": False,
                        "latency": latency,
                        "status": resp.status
                    }
        except Exception as e:
            return {
                "success": False,
                "latency": time.time() - start_time,
                "error": str(e)
            }
    
    async def test_streaming_capacity(self, max_cameras=15):
        """Testa capacidade de streaming simultâneo"""
        print(f"🚀 Iniciando teste de capacidade de streaming...")
        print(f"📹 Testando {min(max_cameras, len(CAMERAS))} câmeras simultâneas")
        
        async with aiohttp.ClientSession() as session:
            # Login
            token = await self.login(session)
            if not token:
                print("❌ Falha no login")
                return
            
            print("✅ Login realizado com sucesso")
            
            # Criar câmeras em lotes
            batch_size = 3
            created_cameras = []
            
            for i in range(0, min(max_cameras, len(CAMERAS)), batch_size):
                batch = CAMERAS[i:i+batch_size]
                print(f"\n📦 Criando lote {i//batch_size + 1} ({len(batch)} câmeras)...")
                
                # Criar câmeras do lote simultaneamente
                tasks = [self.create_camera(session, token, cam) for cam in batch]
                results = await asyncio.gather(*tasks)
                
                for result in results:
                    if result["success"]:
                        created_cameras.append(result)
                        print(f"✅ {result['name']}: Criada em {result['creation_time']:.2f}s")
                    else:
                        print(f"❌ {result['name']}: {result['error']} ({result['creation_time']:.2f}s)")
                
                # Aguardar um pouco entre lotes
                await asyncio.sleep(2)
            
            print(f"\n📊 Câmeras criadas: {len(created_cameras)}/{min(max_cameras, len(CAMERAS))}")
            
            # Aguardar streams ficarem prontos
            print("\n⏳ Aguardando streams ficarem prontos...")
            await asyncio.sleep(10)
            
            # Testar latência de todos os streams simultaneamente
            print("\n🔍 Testando latência dos streams...")
            
            stream_tasks = [
                self.test_hls_stream(session, cam["camera_id"]) 
                for cam in created_cameras
            ]
            
            stream_results = await asyncio.gather(*stream_tasks)
            
            # Análise dos resultados
            successful_streams = [r for r in stream_results if r["success"]]
            failed_streams = [r for r in stream_results if not r["success"]]
            
            if successful_streams:
                avg_latency = sum(r["latency"] for r in successful_streams) / len(successful_streams)
                max_latency = max(r["latency"] for r in successful_streams)
                min_latency = min(r["latency"] for r in successful_streams)
                
                print(f"\n📈 RESULTADOS DE STREAMING:")
                print(f"✅ Streams funcionando: {len(successful_streams)}")
                print(f"❌ Streams com falha: {len(failed_streams)}")
                print(f"⚡ Latência média: {avg_latency:.3f}s")
                print(f"🔺 Latência máxima: {max_latency:.3f}s")
                print(f"🔻 Latência mínima: {min_latency:.3f}s")
                
                # Classificar qualidade
                if avg_latency < 1.0:
                    quality = "🟢 EXCELENTE"
                elif avg_latency < 2.0:
                    quality = "🟡 BOA"
                elif avg_latency < 3.0:
                    quality = "🟠 REGULAR"
                else:
                    quality = "🔴 RUIM"
                
                print(f"🎯 Qualidade geral: {quality}")
                
            else:
                print("❌ Nenhum stream funcionando")
            
            return {
                "total_cameras": len(created_cameras),
                "successful_streams": len(successful_streams),
                "failed_streams": len(failed_streams),
                "avg_latency": avg_latency if successful_streams else 0,
                "max_latency": max_latency if successful_streams else 0,
                "min_latency": min_latency if successful_streams else 0
            }

async def main():
    tester = StreamingTester()
    
    print("=" * 60)
    print("🎬 TESTE DE CAPACIDADE DE STREAMING VMS")
    print("=" * 60)
    
    # Testar com diferentes quantidades
    for camera_count in [5, 10, 15]:
        print(f"\n🔄 Testando com {camera_count} câmeras...")
        result = await tester.test_streaming_capacity(camera_count)
        
        if result:
            print(f"\n📋 RESUMO - {camera_count} câmeras:")
            print(f"   Criadas: {result['total_cameras']}")
            print(f"   Funcionando: {result['successful_streams']}")
            print(f"   Latência média: {result['avg_latency']:.3f}s")
        
        print("\n" + "="*40)
        
        # Aguardar entre testes
        if camera_count < 15:
            print("⏳ Aguardando 30s antes do próximo teste...")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())