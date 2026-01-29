#!/usr/bin/env python3
"""
Monitor de Drift para MediaMTX
Detecta e corrige automaticamente problemas de sincronização.
Sincronizado com as configurações de HLS Low Latency do main.py.
"""

import asyncio
import logging
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class DriftMonitor:
    def __init__(self, mediamtx_api_url: str, auth: Optional[tuple] = None):
        self.api_url = mediamtx_api_url
        self.auth = auth
        # Timeout um pouco maior para operações de rede
        self.client = httpx.AsyncClient(timeout=10.0, auth=auth)
        self.drift_counts: Dict[str, int] = {}
        self.last_reset: Dict[str, datetime] = {}
        
    async def check_streams(self) -> List[str]:
        """Verifica streams com problemas de drift (Readers conectados mas 0 bytes enviados)."""
        try:
            resp = await self.client.get(f"{self.api_url}/v3/paths/list")
            if resp.status_code != 200:
                return []
                
            items = resp.json().get("items", [])
            problematic_streams = []
            
            for item in items:
                path_name = item.get("name", "")
                # Só monitora as câmeras do sistema (cam_*)
                if not path_name.startswith("cam_"):
                    continue
                    
                # Verifica se há readers mas sem bytes sendo enviados
                readers = item.get("readers", [])
                bytes_sent = item.get("bytesSent", 0)
                ready = item.get("ready", False)
                
                # Critério de Drift:
                # 1. Stream diz que está "Ready"
                # 2. Tem gente tentando assistir (Readers > 0)
                # 3. Mas nenhum dado está saindo (bytesSent == 0)
                if ready and len(readers) > 0 and bytes_sent == 0:
                    problematic_streams.append(path_name)
                    logger.warning(f"⚠️ Drift detectado em {path_name}: {len(readers)} readers, 0 bytes enviados.")
                    
            return problematic_streams
            
        except Exception as e:
            logger.error(f"Erro ao verificar streams: {e}")
            return []
    
    async def reset_stream(self, stream_path: str) -> bool:
        """
        Reseta um stream travado.
        IMPORTANTE: Recria usando as configurações de HLS Low Latency.
        """
        try:
            # 1. Obtém a configuração atual para preservar a URL RTSP (source)
            resp = await self.client.get(f"{self.api_url}/v3/paths/get/{stream_path}")
            if resp.status_code != 200:
                return False
                
            current_config = resp.json()
            source = current_config.get("source")
            
            if not source:
                return False
            
            logger.info(f"🔄 Resetando {stream_path}...")

            # 2. Remove o path travado
            await self.client.delete(f"{self.api_url}/v3/config/paths/delete/{stream_path}")
            
            # Aguarda o MediaMTX limpar os recursos
            await asyncio.sleep(2)
            
            # 3. Recria com configurações OTIMIZADAS (Sincronizado com main.py)
            new_config = {
                "source": source,
                "sourceOnDemand": True,
                "sourceOnDemandStartTimeout": "10s", # Rápido para recuperar
                "sourceOnDemandCloseAfter": "30s",   # Igual ao main.py
                "rtspTransport": "tcp",              # TCP para estabilidade
                
                # --- Configurações Cruciais para o Player Frontend ---
                "hlsVariant": "lowLatency",
                "hlsSegmentCount": 5,
                "hlsSegmentDuration": "1s",
                
                # Gravação: Mantemos False para consistência com main.py.
                # Se precisar gravar, mude para True, mas cuidado com disco cheio.
                "record": False,
                # "recordPath": "/recordings/%path/%Y-%m-%d_%H-%M-%S-%f",
                # "recordFormat": "fmp4",
                # "recordPartDuration": "4s",
                # "recordSegmentDuration": "1h",
            }
            
            resp = await self.client.post(
                f"{self.api_url}/v3/config/paths/add/{stream_path}",
                json=new_config
            )
            
            if resp.status_code in [200, 201, 204]:
                self.last_reset[stream_path] = datetime.now()
                logger.info(f"✅ Stream {stream_path} recuperado com sucesso!")
                return True
            else:
                logger.error(f"❌ Falha ao recriar stream {stream_path}: {resp.status_code} - {resp.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro crítico ao resetar {stream_path}: {e}")
            return False
    
    async def monitor_loop(self, interval: int = 30):
        """Loop principal executado em background."""
        logger.info("🔍 Monitor de Drift Iniciado (Verificando a cada 30s)")
        
        while True:
            try:
                problematic_streams = await self.check_streams()
                
                for stream_path in problematic_streams:
                    # Evita resetar o mesmo stream repetidamente em curto período (Cool down)
                    last_reset = self.last_reset.get(stream_path)
                    if last_reset and datetime.now() - last_reset < timedelta(minutes=2):
                        continue
                    
                    # Incrementa contador de falhas
                    self.drift_counts[stream_path] = self.drift_counts.get(stream_path, 0) + 1
                    
                    # Se falhar 2 vezes seguidas, reseta
                    if self.drift_counts[stream_path] >= 2:
                        success = await self.reset_stream(stream_path)
                        if success:
                            self.drift_counts[stream_path] = 0
                
                # Limpa contadores de streams saudáveis
                current_problematic = set(problematic_streams)
                for stream in list(self.drift_counts.keys()):
                    if stream not in current_problematic:
                        self.drift_counts[stream] = 0
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Erro no loop do monitor: {e}")
                await asyncio.sleep(interval)
    
    async def close(self):
        await self.client.aclose()

# Função auxiliar para iniciar junto com o FastAPI
async def start_drift_monitor(mediamtx_api_url: str, auth: Optional[tuple] = None):
    monitor = DriftMonitor(mediamtx_api_url, auth)
    asyncio.create_task(monitor.monitor_loop())
    return monitor