import os
import httpx
from redis.asyncio import Redis
from database import cameras_table

MEDIAMTX_API = os.getenv("MEDIAMTX_API_URL", "http://mediamtx:9997")

class StreamService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def update_cameras_status(self, db_connection):
        """
        Tarefa de fundo: Busca câmeras do DB,
        verifica no MediaMTX e atualiza o Redis.
        """
        try:
            # Busca câmeras no banco (usando SQLAlchemy Core)
            query = cameras_table.select()
            cameras = await db_connection.fetch_all(query)
        except Exception as e:
            print(f"Erro ao buscar câmeras do DB: {e}")
            return

        # Busca streams ativos no MediaMTX
        active_names = set()
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{MEDIAMTX_API}/v3/paths/list")
                if resp.status_code == 200:
                    data = resp.json()
                    # A API do MediaMTX retorna { "items": [ { "name": "..." } ] }
                    items = data.get("items", [])
                    active_names = {item.get("name") for item in items}
        except Exception as e:
            print(f"Erro ao conectar MediaMTX ({MEDIAMTX_API}): {e}")

        # Atualiza o Redis (Pipeline para performance)
        try:
            pipeline = self.redis.pipeline()
            for cam in cameras:
                # Convenção: nome da camera no MediaMTX é 'cam_{id}'
                stream_name = f"cam_{cam['id']}"
                status = "online" if stream_name in active_names else "offline"
                
                # Chave: camera:{id}:status -> "online"
                pipeline.set(f"camera:{cam['id']}:status", status, ex=15)
            
            await pipeline.execute()
        except Exception as e:
            print(f"Erro ao atualizar Redis: {e}")

    async def get_playback_manifest(self, camera_id: int, start: str, end: str):
        # Mock de playback para evitar erros por enquanto
        return "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:10\n#EXT-X-ENDLIST"