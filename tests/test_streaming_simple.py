import asyncio
import aiohttp
import time

class StreamingTester:
    def __init__(self):
        self.base_url = "http://localhost"
        
    async def login(self, session):
        login_data = {"email": "admin@test.com", "password": "admin123"}
        
        async with session.post(f"{self.base_url}/api/auth/login/", json=login_data) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get('access')
            return None
    
    async def get_cameras(self, session, token):
        headers = {"Authorization": f"Bearer {token}"}
        
        async with session.get(f"{self.base_url}/api/cameras/", headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get('results', [])
            return []
    
    async def test_hls_stream(self, session, camera_id):
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
    
    async def test_streaming_capacity(self):
        print("Iniciando teste de streaming...")
        
        async with aiohttp.ClientSession() as session:
            token = await self.login(session)
            if not token:
                print("ERRO: Falha no login")
                return
            
            print("Login realizado")
            
            cameras = await self.get_cameras(session, token)
            print(f"Cameras encontradas: {len(cameras)}")
            
            if not cameras:
                print("Nenhuma camera encontrada")
                return
            
            print("Aguardando streams ficarem prontos...")
            await asyncio.sleep(15)
            
            print("Testando latencia dos streams...")
            
            successful_streams = 0
            failed_streams = 0
            total_latency = 0
            
            for camera in cameras:
                camera_id = camera['id']
                camera_name = camera['name']
                
                result = await self.test_hls_stream(session, camera_id)
                
                if result["success"]:
                    successful_streams += 1
                    total_latency += result["latency"]
                    print(f"  OK: {camera_name} - {result['latency']:.3f}s ({result['segments']} segmentos)")
                else:
                    failed_streams += 1
                    status = result.get('status', 'erro')
                    print(f"  ERRO: {camera_name} - Status {status}")
            
            print(f"\nRESULTADOS:")
            print(f"  Streams funcionando: {successful_streams}")
            print(f"  Streams com falha: {failed_streams}")
            
            if successful_streams > 0:
                avg_latency = total_latency / successful_streams
                print(f"  Latencia media: {avg_latency:.3f}s")
                
                if avg_latency < 1.0:
                    quality = "EXCELENTE"
                elif avg_latency < 2.0:
                    quality = "BOA"
                elif avg_latency < 3.0:
                    quality = "REGULAR"
                else:
                    quality = "RUIM"
                
                print(f"  Qualidade: {quality}")
            
            return {
                "successful_streams": successful_streams,
                "failed_streams": failed_streams,
                "avg_latency": total_latency / successful_streams if successful_streams > 0 else 0
            }

async def main():
    tester = StreamingTester()
    
    print("=" * 50)
    print("TESTE DE STREAMING VMS")
    print("=" * 50)
    
    result = await tester.test_streaming_capacity()
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())