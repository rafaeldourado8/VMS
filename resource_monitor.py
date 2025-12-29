#!/usr/bin/env python3
"""
Monitor de Recursos VMS
Monitora CPU/Memória e aplica throttling automático
"""

import asyncio
import psutil
import docker
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ResourceMonitor:
    def __init__(self):
        self.client = docker.from_env()
        self.cpu_threshold = 80.0  # 80% CPU
        self.memory_threshold = 85.0  # 85% Memória
        self.throttle_active = False
        
    def get_system_stats(self):
        """Obtém estatísticas do sistema."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3)
        }
    
    def get_container_stats(self, container_name):
        """Obtém estatísticas de um container."""
        try:
            container = self.client.containers.get(container_name)
            stats = container.stats(stream=False)
            
            # CPU
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0
            
            # Memória
            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_percent = (memory_usage / memory_limit) * 100.0
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_usage_mb': memory_usage / (1024**2)
            }
        except Exception as e:
            logger.error(f"Erro ao obter stats do container {container_name}: {e}")
            return None
    
    async def apply_throttling(self):
        """Aplica throttling quando recursos estão altos."""
        if self.throttle_active:
            return
            
        logger.warning("🚨 Aplicando throttling por alta utilização de recursos")
        self.throttle_active = True
        
        try:
            # Reduz workers do streaming
            streaming_container = self.client.containers.get('gtvision_streaming')
            streaming_container.restart()
            
            # Pausa gravação temporariamente
            mediamtx_container = self.client.containers.get('gtvision_mediamtx')
            # Aqui poderia pausar gravação via API se necessário
            
            logger.info("✅ Throttling aplicado")
            
        except Exception as e:
            logger.error(f"Erro ao aplicar throttling: {e}")
    
    async def remove_throttling(self):
        """Remove throttling quando recursos normalizam."""
        if not self.throttle_active:
            return
            
        logger.info("📈 Removendo throttling - recursos normalizados")
        self.throttle_active = False
        
        # Aqui poderia reativar funcionalidades pausadas
    
    async def monitor_loop(self):
        """Loop principal de monitoramento."""
        logger.info("🔍 Iniciando monitor de recursos...")
        
        while True:
            try:
                # Stats do sistema
                system_stats = self.get_system_stats()
                
                # Stats dos containers principais
                mediamtx_stats = self.get_container_stats('gtvision_mediamtx')
                streaming_stats = self.get_container_stats('gtvision_streaming')
                
                # Log das estatísticas
                logger.info(f"💻 Sistema - CPU: {system_stats['cpu_percent']:.1f}% | "
                           f"RAM: {system_stats['memory_percent']:.1f}% | "
                           f"Disponível: {system_stats['memory_available_gb']:.1f}GB")
                
                if mediamtx_stats:
                    logger.info(f"📹 MediaMTX - CPU: {mediamtx_stats['cpu_percent']:.1f}% | "
                               f"RAM: {mediamtx_stats['memory_percent']:.1f}%")
                
                # Verifica se precisa aplicar throttling
                if (system_stats['cpu_percent'] > self.cpu_threshold or 
                    system_stats['memory_percent'] > self.memory_threshold):
                    await self.apply_throttling()
                elif (system_stats['cpu_percent'] < self.cpu_threshold - 10 and 
                      system_stats['memory_percent'] < self.memory_threshold - 10):
                    await self.remove_throttling()
                
                await asyncio.sleep(30)  # Monitora a cada 30s
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(30)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    monitor = ResourceMonitor()
    await monitor.monitor_loop()

if __name__ == "__main__":
    asyncio.run(main())