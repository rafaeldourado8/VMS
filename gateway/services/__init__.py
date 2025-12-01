import os
import json
import httpx
from redis.asyncio import Redis
from database import cameras_table

MEDIAMTX_API = os.getenv("MEDIAMTX_API_URL", "http://mediamtx:9997")

class StreamService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def update_cameras_status(self, db_connection):
        """
        Tarefa de fundo: Busca câmeras do DB (Réplica),
        verifica no MediaMTX e atualiza o Redis.
        """
        query = cameras_table.select()
        cameras = await db_connection.fetch_all(query)
        
        # Busca todas as sessões ativas no MediaMTX
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{MEDIAMTX_API}/v3/paths/list")
                if resp.status_code == 200:
                    active_paths = resp.json().get("items", [])
                    # Supondo que o nome do path seja 'cam_{id}' ou o próprio nome da câmera
                    active_names = {p.get("name") for p in active_paths}
                else:
                    active_names = set()
        except Exception as e:
            print(f"Erro ao conectar MediaMTX: {e}")
            active_names = set()

        pipeline = self.redis.pipeline()
        
        for cam in cameras:
            # Lógica de match: Ajuste conforme sua convenção de nomes no MediaMTX
            # Ex: Se a câmera ID 1 publica em rtsp://server/cam_1, o nome é 'cam_1'
            stream_name = f"cam_{cam['id']}" 
            
            # Verifica se está na lista ativa
            is_online = stream_name in active_names
            status = "online" if is_online else "offline"
            
            # Salva no Redis com TTL curto
            pipeline.set(f"camera:{cam['id']}:status", status, ex=10)
            
        await pipeline.execute()

    async def get_playback_manifest(self, camera_id: int, start: str, end: str):
        """
        Gera playlist HLS (.m3u8) para playback.
        """
        # Implementação stub. Em produção, listaria arquivos .ts do disco.
        manifest = "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:10\n#EXT-X-ENDLIST"
        return manifest