# VMS/backend/streaming_integration/client.py
import httpx
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class MediaMTXApiClient:
    """
    Cliente da API HTTP para controlar o MediaMTX dinamicamente.
    """
    def __init__(self):
        try:
            self.base_url = settings.MEDIAMTX_API_URL
            
            # --- CONFIGURAÇÃO DE AUTENTICAÇÃO ---
            # Verifica se as credenciais estão definidas no settings
            self.auth = None
            user = getattr(settings, 'MEDIAMTX_API_USER', None)
            password = getattr(settings, 'MEDIAMTX_API_PASS', None)
            
            if user and password:
                self.auth = (user, password)
                logger.info(f"MediaMTXApiClient: Autenticação configurada para usuário '{user}'")
            else:
                logger.warning("MediaMTXApiClient: Credenciais de API não encontradas no settings. Tentando conexão anônima.")
            
            # Passa a tupla de auth para o cliente
            self.client = httpx.Client(base_url=self.base_url, auth=self.auth, timeout=5.0)
            logger.info(f"MediaMTXApiClient inicializado. Base URL: {self.base_url}")
            
        except AttributeError:
            logger.error("MEDIAMTX_API_URL não está definido no settings.py!")
            self.base_url = None
            self.client = None

    def add_or_update_camera(self, camera_id: str, rtsp_url: str):
        """
        Adiciona ou atualiza a configuração de uma câmara (path) no MediaMTX.
        """
        if not self.client:
            logger.error("Cliente MediaMTX não inicializado.")
            return False

        path_name = str(camera_id)
        # Este é o payload de configuração (o mesmo do .yml, mas em JSON)
        config_payload = {
            "source": "pull",
            "sourceOnDemand": True,
            "sourceOnDemandStartTimeout": "10s",
            "sourceOnDemandCloseAfter": "10s",
            "sourceUrl": rtsp_url
        }
        
        try:
            # A API do MediaMTX usa /v3/config/paths/set/{nome_do_path}
            # (Usamos 'set' em vez de 'add' para que funcione para criar E atualizar)
            response = self.client.post(f"/v3/config/paths/set/{path_name}", json=config_payload)
            response.raise_for_status() # Lança erro se for 4xx ou 5xx
            
            logger.info(f"Câmara {path_name} adicionada/atualizada no MediaMTX.")
            return True
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro da API MediaMTX ao configurar {path_name}: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Erro de HTTP ao contactar MediaMTX para {path_name}: {e}")
        return False

    def remove_camera(self, camera_id: str):
        """
        Remove uma câmara (path) do MediaMTX.
        """
        if not self.client:
            logger.error("Cliente MediaMTX não inicializado.")
            return False

        path_name = str(camera_id)
        
        try:
            # A API do MediaMTX usa /v3/config/paths/remove/{nome_do_path}
            response = self.client.post(f"/v3/config/paths/remove/{path_name}")
            response.raise_for_status()
            
            logger.info(f"Câmara {path_name} removida do MediaMTX.")
            return True

        except httpx.HTTPStatusError as e:
            logger.error(f"Erro da API MediaMTX ao remover {path_name}: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Erro de HTTP ao contactar MediaMTX para {path_name}: {e}")
        return False

# Instancia o novo cliente
mediamtx_api_client = MediaMTXApiClient()