import asyncio
import aiohttp
import json

# Lista completa de câmeras para teste
TEST_CAMERAS = [
    {
        "name": "Camera Teste 1",
        "url": "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0",
        "location": "Teste RTSP 1"
    },
    {
        "name": "Camera Teste 2", 
        "url": "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0",
        "location": "Teste RTSP 2"
    },
    {
        "name": "Camera Teste 3",
        "url": "rtsp://admin:Camerite123@45.236.226.74:6050/cam/realmonitor?channel=1&subtype=0", 
        "location": "Teste RTSP 3"
    },
    {
        "name": "Camera Teste 4",
        "url": "rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0",
        "location": "Teste RTSP 4"
    },
    {
        "name": "Camera Teste 5",
        "url": "rtsp://admin:Camerite123@45.236.226.72:6048/cam/realmonitor?channel=1&subtype=0",
        "location": "Teste RTSP 5"
    }
]

class CameraSetup:
    def __init__(self):
        self.base_url = "http://localhost"
        
    async def login(self, session):
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
                    return {"success": False, "error": f"HTTP {resp.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def setup_test_cameras(self, max_cameras=5):
        print("Configurando cameras de teste no VMS...")
        
        cameras_to_add = TEST_CAMERAS[:max_cameras]
        
        async with aiohttp.ClientSession() as session:
            token = await self.login(session)
            if not token:
                print("ERRO: Falha no login")
                print("Acesse: http://localhost para criar usuario admin")
                return False
            
            print("Login realizado com sucesso")
            print(f"Adicionando {len(cameras_to_add)} cameras...")
            
            success_count = 0
            failed_count = 0
            
            for i, camera in enumerate(cameras_to_add, 1):
                print(f"[{i}/{len(cameras_to_add)}] Adicionando: {camera['name']}")
                
                result = await self.create_camera(session, token, camera)
                
                if result["success"]:
                    success_count += 1
                    camera_id = result["camera"]["id"]
                    print(f"   OK: Criada com ID: {camera_id}")
                else:
                    failed_count += 1
                    print(f"   ERRO: {result['error']}")
                
                await asyncio.sleep(1)
            
            print(f"\nRESUMO:")
            print(f"   Cameras criadas: {success_count}")
            print(f"   Cameras com falha: {failed_count}")
            
            if success_count > 0:
                print(f"\nProximos passos:")
                print(f"   1. Acesse http://localhost")
                print(f"   2. Execute: python tests/test_streaming_capacity.py")
            
            return success_count > 0

async def main():
    setup = CameraSetup()
    
    print("=" * 50)
    print("CONFIGURACAO DE CAMERAS DE TESTE VMS")
    print("=" * 50)
    
    await setup.setup_test_cameras(5)
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())