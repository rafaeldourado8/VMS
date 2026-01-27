import asyncio
import logging
from typing import Set
from infrastructure.servers.mediamtx.adapter import MediaMTXAdapter
from infrastructure.repositories.camera_repository import CameraRepository

logger = logging.getLogger(__name__)

class PathObserver:
    """Monitora paths do MediaMTX e sincroniza com câmeras"""
    
    def __init__(self, mediamtx: MediaMTXAdapter, camera_repo: CameraRepository, interval: int = 10):
        self.mediamtx = mediamtx
        self.camera_repo = camera_repo
        self.interval = interval
        self.known_paths: Set[str] = set()
        self.running = False
    
    async def start(self):
        """Inicia observação contínua"""
        self.running = True
        print("[PathObserver] Started - monitoring every", self.interval, "seconds")
        
        while self.running:
            try:
                await self._sync_paths()
            except Exception as e:
                print(f"[PathObserver] Error: {e}")
            
            await asyncio.sleep(self.interval)
    
    async def stop(self):
        """Para observação"""
        self.running = False
        logger.info("PathObserver stopped")
    
    async def _sync_paths(self):
        """Sincroniza paths do MediaMTX com banco"""
        response = await asyncio.to_thread(self.mediamtx.get_all_paths)
        
        if not response:
            return
        
        current_paths = {item['name'] for item in response.get('items', [])}
        
        new_paths = current_paths - self.known_paths
        for path_name in new_paths:
            await self._on_path_created(path_name)
        
        removed_paths = self.known_paths - current_paths
        for path_name in removed_paths:
            await self._on_path_removed(path_name)
        
        self.known_paths = current_paths
    
    async def _on_path_created(self, path_name: str):
        """Callback quando path é criado"""
        print(f"[PathObserver] Path created: {path_name}")
        
        # Extrai camera_id do path (formato: stream_{camera_id})
        if not path_name.startswith("stream_"):
            return
        
        camera_id_str = path_name.replace("stream_", "")
        
        try:
            from uuid import UUID
            camera_id = UUID(camera_id_str)
            
            # Busca câmera em todas as cidades (não temos city_id aqui)
            # TODO: Adicionar método get_by_public_id_any_city no repository
            
            print(f"[PathObserver] Camera {camera_id} is ONLINE")
            
            # TODO: Se camera.recording_enabled, garantir que está gravando
            # MediaMTX já grava automaticamente (record: yes global)
            
        except Exception as e:
            print(f"[PathObserver] Error processing path {path_name}: {e}")
    
    async def _on_path_removed(self, path_name: str):
        """Callback quando path é removido"""
        print(f"[PathObserver] Path removed: {path_name}")
        
        if not path_name.startswith("stream_"):
            return
        
        camera_id_str = path_name.replace("stream_", "")
        
        try:
            from uuid import UUID
            camera_id = UUID(camera_id_str)
            
            print(f"[PathObserver] Camera {camera_id} is OFFLINE")
            
            # TODO: Atualizar status da câmera para OFFLINE
            # TODO: Limpar sessões ativas no Redis
            
        except Exception as e:
            print(f"[PathObserver] Error processing path {path_name}: {e}")
