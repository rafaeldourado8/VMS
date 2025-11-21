import logging
from django.conf import settings
import httpx
from httpx import BasicAuth

logger = logging.getLogger(__name__)

class MediaMTXApiClient:
    def __init__(self):
        try:
            self.base_url = settings.MEDIAMTX_API_URL.rstrip('/')
            user = getattr(settings, 'MEDIAMTX_API_USER', None)
            password = getattr(settings, 'MEDIAMTX_API_PASS', None)
            
            self.user = user
            self.password = password
            
            self.auth = BasicAuth(user, password) if user and password else None
            self.client = httpx.Client(base_url=self.base_url, auth=self.auth, timeout=10.0)
            logger.info(f"MediaMTXApiClient inicializado. Base URL: {self.base_url}")
        except Exception:
            logger.exception("Erro ao inicializar MediaMTXApiClient")
            self.client = None

    def add_or_update_camera(self, camera_id: str, rtsp_url: str) -> bool:
        if not self.client:
            logger.error("Cliente MediaMTX não inicializado.")
            return False

        path_name = str(camera_id)
        # Usamos localhost pois o FFmpeg roda no mesmo container ou rede que o MediaMTX
        # Se estiverem em containers separados no Docker Compose, 'localhost' no comando FFmpeg
        # refere-se ao container onde o FFmpeg roda (MediaMTX), então está correto se for runOnDemand.
        local_publish_url = f"rtsp://localhost:8554/{path_name}"
        
        if self.user and self.password:
            local_publish_url = f"rtsp://{self.user}:{self.password}@localhost:8554/{path_name}"

        # --- CORREÇÃO DO COMANDO FFMPEG ---
        # 1. -c:v copy: Apenas copia o codec original (H.264), eliminando uso de CPU e latência de encoding.
        # 2. -rtsp_transport tcp: Força TCP na entrada E na saída para evitar perda de pacotes no Docker.
        ffmpeg_cmd = (
            f"ffmpeg -hide_banner -loglevel error "
            f"-rtsp_transport tcp "
            f"-analyzeduration 20000000 -probesize 20000000 "
            f"-i {rtsp_url} "
            f"-c:v copy "
            f"-an " 
            f"-f rtsp "
            f"-rtsp_transport tcp "
            f"{local_publish_url}"
        )

        payload = {
            "source": "publisher",     
            "runOnDemand": ffmpeg_cmd, 
            "runOnDemandRestart": True,
            # Aumentei levemente o timeout para garantir que o stream estabilize antes de falhar
            "runOnDemandStartTimeout": "20s",
            "runOnDemandCloseAfter": "10s",   
        }

        try:
            # 1. Verifica a configuração atual
            check_resp = self.client.get(f"/v3/config/paths/get/{path_name}")
            
            if check_resp.status_code == 200:
                current_config = check_resp.json()
                
                # 2. IDEMPOTÊNCIA: Verifica se o runOnDemand é idêntico
                if current_config.get("runOnDemand") == ffmpeg_cmd:
                    logger.info(f"Câmara {path_name} já está configurada corretamente. Ignorando atualização.")
                    return True

                # Se for diferente, atualiza
                resp = self.client.post(f"/v3/config/paths/replace/{path_name}", json=payload)
                action = "atualizada (Config Alterada)"
            else:
                # Se não existe, cria
                resp = self.client.post(f"/v3/config/paths/add/{path_name}", json=payload)
                action = "adicionada (Nova)"

            resp.raise_for_status()
            logger.info(f"Câmara {path_name} {action} no MediaMTX com sucesso.")
            return True

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400 and "already exists" in e.response.text:
                # Fallback raro para condição de corrida
                return True
            logger.error(f"Erro da API MediaMTX: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Erro ao contactar MediaMTX: {e}")
        return False

    def remove_camera(self, camera_id: str) -> bool:
        if not self.client: return False
        try:
            self.client.delete(f"/v3/config/paths/delete/{camera_id}")
            return True
        except Exception:
            return False

mediamtx_api_client = MediaMTXApiClient()