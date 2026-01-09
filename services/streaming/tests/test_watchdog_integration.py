"""
Script de teste de integracao do Watchdog
Simula comportamento real de streams congelados
"""
import asyncio
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class MockWatchdog:
    """Mock simplificado do watchdog para teste de integracao"""
    
    CHECK_INTERVAL = 5  # Reduzido para teste rapido
    FROZEN_THRESHOLD = 10
    
    def __init__(self):
        self.frame_timestamps = {}
        self.frozen_events = []
        self.running = False
    
    def update_frame(self, camera_id: str):
        """Atualiza timestamp do ultimo frame"""
        self.frame_timestamps[camera_id] = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] Frame recebido: {camera_id}")
    
    async def check_streams(self):
        """Verifica streams congelados"""
        current_time = time.time()
        
        for camera_id, last_frame_time in list(self.frame_timestamps.items()):
            elapsed = current_time - last_frame_time
            
            if elapsed > self.FROZEN_THRESHOLD:
                print(f"[{time.strftime('%H:%M:%S')}] ALERTA: Stream congelado - {camera_id} ({elapsed:.1f}s)")
                self.frozen_events.append({
                    'camera_id': camera_id,
                    'timestamp': current_time,
                    'elapsed': elapsed
                })
                del self.frame_timestamps[camera_id]
    
    async def monitor_loop(self):
        """Loop de monitoramento"""
        while self.running:
            await self.check_streams()
            await asyncio.sleep(self.CHECK_INTERVAL)
    
    async def start(self):
        """Inicia watchdog"""
        self.running = True
        print(f"[{time.strftime('%H:%M:%S')}] Watchdog iniciado")
        print(f"  - Intervalo de verificacao: {self.CHECK_INTERVAL}s")
        print(f"  - Threshold de congelamento: {self.FROZEN_THRESHOLD}s")
        print()
        await self.monitor_loop()
    
    def stop(self):
        """Para watchdog"""
        self.running = False
        print(f"\n[{time.strftime('%H:%M:%S')}] Watchdog parado")


async def simulate_normal_stream(watchdog: MockWatchdog, camera_id: str, duration: int):
    """Simula stream normal com frames regulares"""
    print(f"[{time.strftime('%H:%M:%S')}] Iniciando stream normal: {camera_id}")
    
    end_time = time.time() + duration
    while time.time() < end_time and watchdog.running:
        watchdog.update_frame(camera_id)
        await asyncio.sleep(2)  # Frame a cada 2s


async def simulate_frozen_stream(watchdog: MockWatchdog, camera_id: str, freeze_after: int):
    """Simula stream que congela apos X segundos"""
    print(f"[{time.strftime('%H:%M:%S')}] Iniciando stream que congelara: {camera_id}")
    
    # Envia frames normalmente
    for _ in range(freeze_after // 2):
        watchdog.update_frame(camera_id)
        await asyncio.sleep(2)
    
    # Para de enviar frames (simula congelamento)
    print(f"[{time.strftime('%H:%M:%S')}] Stream congelou: {camera_id}")
    await asyncio.sleep(20)  # Aguarda deteccao


async def test_scenario_1():
    """Cenario 1: Stream normal sem congelamento"""
    print("=" * 60)
    print("CENARIO 1: Stream Normal")
    print("=" * 60)
    
    watchdog = MockWatchdog()
    
    # Inicia watchdog
    watchdog_task = asyncio.create_task(watchdog.start())
    
    # Simula stream normal por 20s
    await simulate_normal_stream(watchdog, "cam1", 20)
    
    # Para watchdog
    watchdog.stop()
    await asyncio.sleep(1)
    
    # Verifica resultado
    assert len(watchdog.frozen_events) == 0, "Nao deve ter eventos de congelamento"
    print("\n[OK] Cenario 1: Nenhum congelamento detectado")
    print()


async def test_scenario_2():
    """Cenario 2: Stream que congela"""
    print("=" * 60)
    print("CENARIO 2: Stream Congelado")
    print("=" * 60)
    
    watchdog = MockWatchdog()
    
    # Inicia watchdog
    watchdog_task = asyncio.create_task(watchdog.start())
    
    # Simula stream que congela apos 6s
    await simulate_frozen_stream(watchdog, "cam2", 6)
    
    # Para watchdog
    watchdog.stop()
    await asyncio.sleep(1)
    
    # Verifica resultado
    assert len(watchdog.frozen_events) > 0, "Deve ter detectado congelamento"
    assert watchdog.frozen_events[0]['camera_id'] == "cam2"
    print(f"\n[OK] Cenario 2: Congelamento detectado apos {watchdog.frozen_events[0]['elapsed']:.1f}s")
    print()


async def test_scenario_3():
    """Cenario 3: Multiplas cameras com comportamentos diferentes"""
    print("=" * 60)
    print("CENARIO 3: Multiplas Cameras")
    print("=" * 60)
    
    watchdog = MockWatchdog()
    
    # Inicia watchdog
    watchdog_task = asyncio.create_task(watchdog.start())
    
    # Inicia multiplas cameras
    tasks = [
        asyncio.create_task(simulate_normal_stream(watchdog, "cam1", 25)),
        asyncio.create_task(simulate_frozen_stream(watchdog, "cam2", 6)),
        asyncio.create_task(simulate_frozen_stream(watchdog, "cam3", 8)),
    ]
    
    # Aguarda todas as tasks
    await asyncio.gather(*tasks)
    
    # Para watchdog
    watchdog.stop()
    await asyncio.sleep(1)
    
    # Verifica resultado
    frozen_cameras = [e['camera_id'] for e in watchdog.frozen_events]
    assert "cam2" in frozen_cameras, "cam2 deve ter congelado"
    assert "cam3" in frozen_cameras, "cam3 deve ter congelado"
    assert "cam1" not in frozen_cameras, "cam1 nao deve ter congelado"
    
    print(f"\n[OK] Cenario 3: {len(watchdog.frozen_events)} cameras congeladas detectadas")
    print(f"  - Cameras congeladas: {frozen_cameras}")
    print()


async def main():
    """Executa todos os cenarios de teste"""
    print("\n" + "=" * 60)
    print("TESTE DE INTEGRACAO: WATCHDOG")
    print("=" * 60)
    print()
    
    try:
        await test_scenario_1()
        await test_scenario_2()
        await test_scenario_3()
        
        print("=" * 60)
        print("TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n[ERRO] Teste falhou: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERRO] Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
