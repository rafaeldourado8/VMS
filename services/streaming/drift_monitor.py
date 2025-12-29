#!/usr/bin/env python3
"""
Monitor de Drift para MediaMTX
Detecta e corrige automaticamente problemas de sincronização
"""

import asyncio
import logging
import httpx
from datetime import datetime, timedelta
from typing import Dict, List
import json

logger = logging.getLogger(__name__)

class DriftMonitor:
    def __init__(self, mediamtx_api_url: str, auth: tuple):
        self.api_url = mediamtx_api_url
        self.auth = auth
        self.client = httpx.AsyncClient(timeout=10.0, auth=auth)
        self.drift_counts: Dict[str, int] = {}
        self.last_reset: Dict[str, datetime] = {}
        
    async def check_streams(self) -> List[str]:
        """Verifica streams com problemas de drift."""
        try:
            resp = await self.client.get(f"{self.api_url}/v3/paths/list")
            if resp.status_code != 200:
                return []
                
            items = resp.json().get("items", [])
            problematic_streams = []
            
            for item in items:
                path_name = item.get("name", "")
                if not path_name.startswith("cam_"):
                    continue
                    
                # Verifica se há readers mas sem bytes sendo enviados
                readers = item.get("readers", [])
                bytes_sent = item.get("bytesSent", 0)
                ready = item.get("ready", False)
                
                if ready and len(readers) > 0 and bytes_sent == 0:
                    problematic_streams.append(path_name)
                    logger.warning(f"Stream {path_name} com possível drift: readers={len(readers)}, bytes={bytes_sent}")
                    
            return problematic_streams
            
        except Exception as e:
            logger.error(f"Erro ao verificar streams: {e}")
            return []
    
    async def reset_stream(self, stream_path: str) -> bool:
        """Reseta um stream com drift."""
        try:
            # Primeiro, obtém a configuração atual
            resp = await self.client.get(f"{self.api_url}/v3/paths/get/{stream_path}")
            if resp.status_code != 200:
                return False
                
            config = resp.json()
            source = config.get("source")
            
            if not source:
                return False
            
            # Remove o path
            await self.client.delete(f"{self.api_url}/v3/config/paths/delete/{stream_path}")
            await asyncio.sleep(2)
            
            # Recria com configurações otimizadas
            new_config = {
                "source": source,
                "sourceOnDemand": True,
                "sourceOnDemandStartTimeout": "30s",
                "sourceOnDemandCloseAfter": "60s",
                "rtspTransport": "tcp",
                "rtspUDPReadBufferSize": 33554432,
                "useAbsoluteTimestamp": False,
                "record": True,
                "recordPath": "/recordings/%path/%Y-%m-%d_%H-%M-%S-%f",
                "recordFormat": "fmp4",
                "recordPartDuration": "4s",
                "recordSegmentDuration": "30m",
                "maxReaders": 10
            }
            
            resp = await self.client.post(
                f"{self.api_url}/v3/config/paths/add/{stream_path}",
                json=new_config
            )
            
            if resp.status_code in [200, 201]:
                self.last_reset[stream_path] = datetime.now()
                logger.info(f"✅ Stream {stream_path} resetado com sucesso")
                return True
            else:
                logger.error(f"❌ Falha ao recriar stream {stream_path}: {resp.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao resetar stream {stream_path}: {e}")
            return False
    
    async def monitor_loop(self, interval: int = 60):
        """Loop principal de monitoramento."""
        logger.info("🔍 Iniciando monitor de drift...")
        
        while True:
            try:
                problematic_streams = await self.check_streams()
                
                for stream_path in problematic_streams:
                    # Evita reset muito frequente
                    last_reset = self.last_reset.get(stream_path)
                    if last_reset and datetime.now() - last_reset < timedelta(minutes=5):
                        continue
                    
                    # Incrementa contador de drift
                    self.drift_counts[stream_path] = self.drift_counts.get(stream_path, 0) + 1
                    
                    # Reset após 3 detecções consecutivas
                    if self.drift_counts[stream_path] >= 3:
                        logger.warning(f"🔄 Resetando stream {stream_path} devido a drift persistente")
                        success = await self.reset_stream(stream_path)
                        if success:
                            self.drift_counts[stream_path] = 0
                
                # Limpa contadores de streams que voltaram ao normal
                current_streams = set(problematic_streams)
                for stream_path in list(self.drift_counts.keys()):
                    if stream_path not in current_streams:
                        self.drift_counts[stream_path] = 0
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(interval)
    
    async def close(self):
        await self.client.aclose()

# Integração com o serviço principal
async def start_drift_monitor(mediamtx_api_url: str, auth: tuple):
    """Inicia o monitor de drift em background."""
    monitor = DriftMonitor(mediamtx_api_url, auth)
    
    # Executa em background
    asyncio.create_task(monitor.monitor_loop(interval=30))
    
    return monitor