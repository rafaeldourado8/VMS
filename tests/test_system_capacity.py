import asyncio
import aiohttp
import psutil
import time
import json
from datetime import datetime

class SystemCapacityTester:
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
    
    def get_system_resources(self):
        """Obtém recursos do sistema"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "disk_usage_percent": psutil.disk_usage('/').percent if hasattr(psutil.disk_usage('/'), 'percent') else 0
        }
    
    async def get_docker_stats(self):
        """Obtém estatísticas dos containers Docker"""
        try:
            import subprocess
            
            # Obter stats dos containers
            result = subprocess.run([
                "docker", "stats", "--no-stream", "--format", 
                "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                containers = []
                
                for line in lines:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 4:
                            containers.append({
                                "name": parts[0],
                                "cpu": parts[1],
                                "memory": parts[2],
                                "memory_percent": parts[3]
                            })
                
                return containers
            
        except Exception as e:
            print(f"Erro ao obter stats Docker: {e}")
        
        return []
    
    async def test_mediamtx_capacity(self):
        """Testa capacidade do MediaMTX"""
        try:
            async with aiohttp.ClientSession() as session:
                # Obter estatísticas do MediaMTX
                async with session.get("http://localhost:9997/v3/paths/list") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        paths = data.get('items', [])
                        
                        active_streams = 0
                        total_readers = 0
                        
                        for path in paths:
                            if path.get('ready', False):
                                active_streams += 1
                                total_readers += path.get('readers', 0)
                        
                        return {
                            "total_paths": len(paths),
                            "active_streams": active_streams,
                            "total_readers": total_readers
                        }
        except Exception as e:
            print(f"Erro ao testar MediaMTX: {e}")
        
        return {"total_paths": 0, "active_streams": 0, "total_readers": 0}
    
    async def stress_test_cameras(self, session, token, max_cameras=50):
        """Teste de stress com múltiplas câmeras"""
        print(f"🔥 Iniciando teste de stress com até {max_cameras} câmeras...")
        
        # URLs de teste (repetindo as disponíveis)
        test_urls = [
            "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0",
            "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0",
            "rtsp://admin:Camerite123@45.236.226.74:6050/cam/realmonitor?channel=1&subtype=0",
            "rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0",
            "rtsp://admin:Camerite123@45.236.226.72:6048/cam/realmonitor?channel=1&subtype=0"
        ]
        
        created_cameras = []
        failed_cameras = []
        
        headers = {"Authorization": f"Bearer {token}"}
        
        for i in range(max_cameras):
            # Usar URLs ciclicamente
            url = test_urls[i % len(test_urls)]
            
            camera_data = {
                "name": f"Stress Test Camera {i+1}",
                "stream_url": url,
                "location": f"Teste Stress {i+1}"
            }
            
            start_time = time.time()
            
            try:
                async with session.post(f"{self.base_url}/api/cameras/", 
                                      json=camera_data, headers=headers) as resp:
                    creation_time = time.time() - start_time
                    
                    if resp.status == 201:
                        data = await resp.json()
                        created_cameras.append({
                            "id": data["id"],
                            "name": camera_data["name"],
                            "creation_time": creation_time
                        })
                        print(f"✅ Câmera {i+1}: Criada em {creation_time:.2f}s")
                    else:
                        failed_cameras.append({
                            "name": camera_data["name"],
                            "error": f"HTTP {resp.status}",
                            "creation_time": creation_time
                        })
                        print(f"❌ Câmera {i+1}: Falha HTTP {resp.status}")
                        
            except Exception as e:
                failed_cameras.append({
                    "name": camera_data["name"],
                    "error": str(e),
                    "creation_time": time.time() - start_time
                })
                print(f"❌ Câmera {i+1}: Erro {str(e)}")
            
            # Verificar recursos do sistema a cada 10 câmeras
            if (i + 1) % 10 == 0:
                resources = self.get_system_resources()
                print(f"\n📊 Recursos após {i+1} câmeras:")
                print(f"   CPU: {resources['cpu_percent']:.1f}%")
                print(f"   RAM: {resources['memory_percent']:.1f}%")
                
                # Parar se recursos estão muito altos
                if resources['cpu_percent'] > 90 or resources['memory_percent'] > 90:
                    print(f"⚠️ Recursos críticos atingidos - parando teste")
                    break
                
                # Aguardar um pouco entre lotes
                await asyncio.sleep(2)
        
        return {
            "created": len(created_cameras),
            "failed": len(failed_cameras),
            "total_attempted": len(created_cameras) + len(failed_cameras),
            "created_cameras": created_cameras,
            "failed_cameras": failed_cameras
        }
    
    async def test_system_capacity(self):
        """Teste completo de capacidade do sistema"""
        print("🚀 Iniciando teste de capacidade máxima do sistema...")
        
        # Recursos iniciais
        initial_resources = self.get_system_resources()
        print(f"\n📊 Recursos iniciais:")
        print(f"   CPU: {initial_resources['cpu_percent']:.1f}%")
        print(f"   RAM: {initial_resources['memory_percent']:.1f}% ({initial_resources['memory_available_gb']:.1f}GB disponível)")
        
        # Stats Docker iniciais
        initial_docker = await self.get_docker_stats()
        print(f"\n🐳 Containers Docker ativos: {len(initial_docker)}")
        
        # MediaMTX inicial
        initial_mediamtx = await self.test_mediamtx_capacity()
        print(f"📺 MediaMTX - Streams ativos: {initial_mediamtx['active_streams']}")
        
        async with aiohttp.ClientSession() as session:
            # Login
            token = await self.login(session)
            if not token:
                print("❌ Falha no login")
                return
            
            print("✅ Login realizado")
            
            # Teste de stress progressivo
            results = []
            
            for camera_count in [10, 25, 50, 100]:
                print(f"\n🔥 Testando com {camera_count} câmeras...")
                
                start_time = time.time()
                stress_result = await self.stress_test_cameras(session, token, camera_count)
                test_duration = time.time() - start_time
                
                # Aguardar streams ficarem prontos
                print("⏳ Aguardando streams ficarem prontos...")
                await asyncio.sleep(15)
                
                # Recursos após teste
                final_resources = self.get_system_resources()
                final_mediamtx = await self.test_mediamtx_capacity()
                final_docker = await self.get_docker_stats()
                
                result = {
                    "camera_count": camera_count,
                    "created": stress_result["created"],
                    "failed": stress_result["failed"],
                    "success_rate": (stress_result["created"] / camera_count) * 100,
                    "test_duration": test_duration,
                    "resources": final_resources,
                    "mediamtx": final_mediamtx,
                    "docker_containers": len(final_docker)
                }
                
                results.append(result)
                
                print(f"\n📊 RESULTADO - {camera_count} câmeras:")
                print(f"   ✅ Criadas: {result['created']}")
                print(f"   ❌ Falharam: {result['failed']}")
                print(f"   📈 Taxa de sucesso: {result['success_rate']:.1f}%")
                print(f"   ⏱️ Duração: {result['test_duration']:.1f}s")
                print(f"   💻 CPU: {result['resources']['cpu_percent']:.1f}%")
                print(f"   🧠 RAM: {result['resources']['memory_percent']:.1f}%")
                print(f"   📺 Streams ativos: {result['mediamtx']['active_streams']}")
                
                # Parar se taxa de sucesso muito baixa
                if result['success_rate'] < 50:
                    print(f"⚠️ Taxa de sucesso baixa - parando testes")
                    break
                
                # Parar se recursos críticos
                if result['resources']['cpu_percent'] > 85 or result['resources']['memory_percent'] > 85:
                    print(f"⚠️ Recursos críticos - parando testes")
                    break
            
            # Análise final
            print(f"\n" + "="*60)
            print(f"📋 ANÁLISE FINAL DE CAPACIDADE")
            print(f"="*60)
            
            if results:
                best_result = max(results, key=lambda x: x['created'])
                
                print(f"🏆 Melhor resultado:")
                print(f"   📹 Câmeras simultâneas: {best_result['created']}")
                print(f"   📈 Taxa de sucesso: {best_result['success_rate']:.1f}%")
                print(f"   💻 CPU utilizada: {best_result['resources']['cpu_percent']:.1f}%")
                print(f"   🧠 RAM utilizada: {best_result['resources']['memory_percent']:.1f}%")
                
                # Estimativa de capacidade máxima
                if best_result['resources']['cpu_percent'] < 70:
                    estimated_max = int(best_result['created'] * 1.5)
                elif best_result['resources']['cpu_percent'] < 85:
                    estimated_max = int(best_result['created'] * 1.2)
                else:
                    estimated_max = best_result['created']
                
                print(f"\n🎯 CAPACIDADE ESTIMADA:")
                print(f"   📹 Máximo recomendado: {estimated_max} câmeras")
                print(f"   ⚡ Qualidade: {'🟢 ALTA' if best_result['resources']['cpu_percent'] < 60 else '🟡 MÉDIA' if best_result['resources']['cpu_percent'] < 80 else '🔴 BAIXA'}")
                
                return {
                    "max_cameras_tested": best_result['created'],
                    "estimated_capacity": estimated_max,
                    "peak_cpu": best_result['resources']['cpu_percent'],
                    "peak_memory": best_result['resources']['memory_percent'],
                    "results": results
                }

async def main():
    tester = SystemCapacityTester()
    
    print("=" * 60)
    print("🔥 TESTE DE CAPACIDADE MÁXIMA DO SISTEMA VMS")
    print("=" * 60)
    
    result = await tester.test_system_capacity()
    
    if result:
        print(f"\n🎯 CONCLUSÃO:")
        print(f"   Sistema testado até: {result['max_cameras_tested']} câmeras")
        print(f"   Capacidade estimada: {result['estimated_capacity']} câmeras")
        print(f"   CPU máxima: {result['peak_cpu']:.1f}%")
        print(f"   RAM máxima: {result['peak_memory']:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())