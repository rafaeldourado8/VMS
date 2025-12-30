import asyncio
import aiohttp
import json

# Lista completa de câmeras para teste
TEST_CAMERAS = [
    {
        "name": "Câmera Teste 1",
        "url": "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0",
        "location": "Teste RTSP 1"
    },
    {
        "name": "Câmera Teste 2", 
        "url": "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0",
        "location": "Teste RTSP 2"
    },
    {
        "name": "Câmera Teste 3",
        "url": "rtsp://admin:Camerite123@45.236.226.74:6050/cam/realmonitor?channel=1&subtype=0", 
        "location": "Teste RTSP 3"
    },
    {
        "name": "Câmera Teste 4",
        "url": "rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0",
        "location": "Teste RTSP 4"
    },
    {
        "name": "Câmera Teste 5",
        "url": "rtsp://admin:Camerite123@45.236.226.72:6048/cam/realmonitor?channel=1&subtype=0",
        "location": "Teste RTSP 5"
    },
    {
        "name": "Câmera Teste 6",
        "url": "rtsp://admin:Camerite123@45.236.226.71:6047/cam/realmonitor?channel=1&subtype=0",
        "location": "Teste RTSP 6"
    },
    {
        "name": "Câmera Teste 7",
        "url": "rtsp://admin:Camerite123@45.236.226.71:6046/cam/realmonitor?channel=1&subtype=0",
        "location": "Teste RTSP 7"
    },
    {
        "name": "Câmera Teste 8",
        "url": "rtsp://admin:Camerite123@45.236.226.70:6045/cam/realmonitor?channel=1&subtype=0",
        "location": "Teste RTSP 8"
    },
    {
        "name": "Câmera Teste 9",
        "url": "rtsp://admin:Camerite123@45.236.226.70:6044/cam/realmonitor?channel=1&subtype=0",
        "location": "Teste RTSP 9"
    },
    {
        "name": "Câmera RTMP 1",
        "url": "rtmp://inst-iwvio-srs-rtmp-intelbras.camerite.services:1935/record/7KOM27157189T.stream",
        "location": "Teste RTMP 1"
    },
    {
        "name": "Câmera Teste 11",
        "url": "rtsp://admin:Camerite@186.226.193.111:602/h264/ch1/main/av_stream",
        "location": "Teste RTSP 11"
    },
    {
        "name": "Câmera Teste 12", 
        "url": "rtsp://admin:Camerite@186.226.193.111:601/h264/ch1/main/av_stream",
        "location": "Teste RTSP 12"
    },
    {
        "name": "Câmera Teste 13",
        "url": "rtsp://admin:Camerite@170.84.217.84:603/h264/ch1/main/av_stream",
        "location": "Teste RTSP 13"
    },
    {
        "name": "Câmera RTMP 2",
        "url": "rtmp://inst-czd17-srs-rtmp-hik-pro-connect.camerite.services:1935/record/FC2487833.stream",
        "location": "Teste RTMP 2"
    },
    {
        "name": "Câmera RTMP 3",
        "url": "rtmp://inst-czd17-srs-rtmp-hik-pro-connect.camerite.services:1935/record/FC2487237.stream", 
        "location": "Teste RTMP 3"
    }
]

class CameraSetup:
    def __init__(self):
        self.base_url = "http://localhost"
        
    async def login(self, session):
        """Faz login no sistema"""
        login_data = {
            "email": "admin@test.com",
            "password": "admin123"
        }
        
        try:
            async with session.post(f"{self.base_url}/api/auth/login/", json=login_data) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('access')
        except:
            pass
        return None
    
    async def create_camera(self, session, token, camera_data):
        """Cria uma câmera via API"""
        headers = {"Authorization": f"Bearer {token}"}
        
        payload = {
            "name": camera_data["name"],
            "stream_url": camera_data["url"], 
            "location": camera_data["location"]
        }
        
        try:
            async with session.post(f"{self.base_url}/api/cameras/", 
                                  json=payload, headers=headers) as resp:
                if resp.status == 201:
                    data = await resp.json()
                    return {"success": True, "camera": data}
                else:
                    error_text = await resp.text()
                    return {"success": False, "error": f"HTTP {resp.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def setup_test_cameras(self, max_cameras=None):
        """Configura câmeras de teste no sistema"""
        print("🚀 Configurando câmeras de teste no VMS...")
        
        cameras_to_add = TEST_CAMERAS[:max_cameras] if max_cameras else TEST_CAMERAS
        
        async with aiohttp.ClientSession() as session:
            # Login
            token = await self.login(session)
            if not token:
                print("❌ Falha no login - verifique se o sistema está rodando")
                print("   Acesse: http://localhost para criar usuário admin")
                return False
            
            print("✅ Login realizado com sucesso")
            print(f"📹 Adicionando {len(cameras_to_add)} câmeras...")
            
            success_count = 0
            failed_count = 0
            
            for i, camera in enumerate(cameras_to_add, 1):
                print(f"\n📹 [{i}/{len(cameras_to_add)}] Adicionando: {camera['name']}")
                
                result = await self.create_camera(session, token, camera)
                
                if result["success"]:
                    success_count += 1
                    camera_id = result["camera"]["id"]
                    print(f"   ✅ Criada com ID: {camera_id}")
                else:
                    failed_count += 1
                    print(f"   ❌ Erro: {result['error']}")
                
                # Aguardar um pouco entre câmeras
                await asyncio.sleep(1)
            
            print(f"\n📊 RESUMO:")
            print(f"   ✅ Câmeras criadas: {success_count}")
            print(f"   ❌ Câmeras com falha: {failed_count}")
            print(f"   📈 Taxa de sucesso: {(success_count/len(cameras_to_add)*100):.1f}%")
            
            if success_count > 0:
                print(f"\n🎯 Próximos passos:")
                print(f"   1. Acesse http://localhost para ver as câmeras")
                print(f"   2. Execute os testes: python tests/run_all_tests.bat")
                print(f"   3. Aguarde alguns minutos para streams ficarem prontos")
            
            return success_count > 0

async def main():
    setup = CameraSetup()
    
    print("=" * 60)
    print("CONFIGURACAO DE CAMERAS DE TESTE VMS")
    print("=" * 60)
    
    # Perguntar quantas câmeras adicionar
    try:
        max_cameras = input("Quantas cameras adicionar? (Enter para todas as 15): ").strip()
        if max_cameras:
            max_cameras = int(max_cameras)
        else:
            max_cameras = None
    except:
        max_cameras = None
    
    await setup.setup_test_cameras(max_cameras)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())