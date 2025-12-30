import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta

class DetectionTester:
    def __init__(self):
        self.base_url = "http://localhost"
        
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
    
    async def get_cameras(self, session, token):
        """Lista câmeras do sistema"""
        headers = {"Authorization": f"Bearer {token}"}
        
        async with session.get(f"{self.base_url}/api/cameras/", headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            return []
    
    async def get_detections(self, session, token, camera_id=None):
        """Obtém detecções do sistema"""
        headers = {"Authorization": f"Bearer {token}"}
        
        params = {}
        if camera_id:
            params['camera_id'] = camera_id
            
        async with session.get(f"{self.base_url}/api/detections/", 
                             headers=headers, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get('results', [])
            return []
    
    async def check_ai_workers(self):
        """Verifica se os AI workers estão ativos"""
        try:
            # Verificar logs dos workers via Docker
            import subprocess
            
            # Worker 1
            result1 = subprocess.run([
                "docker-compose", "logs", "--tail=5", "ai_worker_1"
            ], capture_output=True, text=True, cwd="d:/VMS")
            
            # Worker 2  
            result2 = subprocess.run([
                "docker-compose", "logs", "--tail=5", "ai_worker_2"
            ], capture_output=True, text=True, cwd="d:/VMS")
            
            worker1_active = "pronto para processar frames" in result1.stdout
            worker2_active = "pronto para processar frames" in result2.stdout
            
            return {
                "worker1_active": worker1_active,
                "worker2_active": worker2_active,
                "worker1_logs": result1.stdout.split('\n')[-3:],
                "worker2_logs": result2.stdout.split('\n')[-3:]
            }
            
        except Exception as e:
            return {
                "worker1_active": False,
                "worker2_active": False,
                "error": str(e)
            }
    
    async def test_detection_system(self):
        """Testa sistema de detecções"""
        print("🤖 Iniciando teste do sistema de detecções...")
        
        # Verificar AI workers
        print("\n🔍 Verificando AI Workers...")
        worker_status = await self.check_ai_workers()
        
        if worker_status.get("worker1_active"):
            print("✅ AI Worker 1: Ativo")
        else:
            print("❌ AI Worker 1: Inativo")
            
        if worker_status.get("worker2_active"):
            print("✅ AI Worker 2: Ativo")
        else:
            print("❌ AI Worker 2: Inativo")
        
        if not (worker_status.get("worker1_active") or worker_status.get("worker2_active")):
            print("⚠️ Nenhum AI Worker ativo - detecções não funcionarão")
            return False
        
        async with aiohttp.ClientSession() as session:
            # Login
            token = await self.login(session)
            if not token:
                print("❌ Falha no login")
                return False
            
            print("✅ Login realizado")
            
            # Listar câmeras
            cameras = await self.get_cameras(session, token)
            print(f"📹 Câmeras encontradas: {len(cameras)}")
            
            if not cameras:
                print("⚠️ Nenhuma câmera encontrada")
                return False
            
            # Verificar detecções existentes
            print("\n🔍 Verificando detecções existentes...")
            
            total_detections = 0
            recent_detections = 0
            now = datetime.now()
            last_hour = now - timedelta(hours=1)
            
            for camera in cameras[:5]:  # Testar primeiras 5 câmeras
                detections = await self.get_detections(session, token, camera['id'])
                camera_recent = 0
                
                for detection in detections:
                    total_detections += 1
                    detection_time = datetime.fromisoformat(detection['timestamp'].replace('Z', '+00:00'))
                    
                    if detection_time > last_hour:
                        recent_detections += 1
                        camera_recent += 1
                
                status = "🟢 ATIVA" if camera_recent > 0 else "🔴 INATIVA"
                print(f"   📹 {camera['name']}: {len(detections)} total, {camera_recent} última hora {status}")
            
            print(f"\n📊 RESUMO DE DETECÇÕES:")
            print(f"   Total de detecções: {total_detections}")
            print(f"   Detecções na última hora: {recent_detections}")
            
            # Classificar atividade
            if recent_detections > 10:
                activity = "🟢 ALTA"
            elif recent_detections > 5:
                activity = "🟡 MÉDIA"
            elif recent_detections > 0:
                activity = "🟠 BAIXA"
            else:
                activity = "🔴 NENHUMA"
            
            print(f"   Atividade de detecção: {activity}")
            
            # Testar configurações de detecção
            print(f"\n⚙️ Testando configurações de detecção...")
            
            for camera in cameras[:3]:  # Testar primeiras 3
                # Verificar se tem configurações de ROI, linhas virtuais, etc.
                roi_areas = camera.get('roi_areas', [])
                virtual_lines = camera.get('virtual_lines', [])
                zone_triggers = camera.get('zone_triggers', [])
                
                config_status = []
                if roi_areas:
                    config_status.append(f"ROI: {len(roi_areas)}")
                if virtual_lines:
                    config_status.append(f"Linhas: {len(virtual_lines)}")
                if zone_triggers:
                    config_status.append(f"Zonas: {len(zone_triggers)}")
                
                config_text = ", ".join(config_status) if config_status else "Padrão"
                print(f"   📹 {camera['name']}: {config_text}")
            
            return {
                "workers_active": worker_status.get("worker1_active") or worker_status.get("worker2_active"),
                "total_cameras": len(cameras),
                "total_detections": total_detections,
                "recent_detections": recent_detections,
                "activity_level": activity
            }

async def main():
    tester = DetectionTester()
    
    print("=" * 60)
    print("🤖 TESTE DO SISTEMA DE DETECÇÕES VMS")
    print("=" * 60)
    
    result = await tester.test_detection_system()
    
    if result:
        print(f"\n📋 RESULTADO FINAL:")
        print(f"   AI Workers ativos: {'✅ SIM' if result['workers_active'] else '❌ NÃO'}")
        print(f"   Câmeras monitoradas: {result['total_cameras']}")
        print(f"   Total de detecções: {result['total_detections']}")
        print(f"   Detecções recentes: {result['recent_detections']}")
        print(f"   Nível de atividade: {result['activity_level']}")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        
        if not result['workers_active']:
            print("   🔧 Verificar e reiniciar AI Workers")
            
        if result['recent_detections'] == 0:
            print("   📹 Verificar se câmeras têm movimento/veículos")
            print("   ⚙️ Configurar zonas de detecção (ROI, linhas virtuais)")
            
        if result['total_cameras'] == 0:
            print("   📹 Adicionar câmeras ao sistema")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())