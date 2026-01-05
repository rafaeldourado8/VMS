import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class MediaMTXClient:
    """Cliente HTTP para MediaMTX API"""
    
    def __init__(self, base_url: str = "http://mediamtx:9997", timeout: float = 10.0, username: Optional[str] = None, password: Optional[str] = None):
        self.base_url = base_url
        self.timeout = timeout
        self.auth = (username, password) if username and password else None
    
    def add_path(self, path: str, rtsp_url: str, on_demand: bool = True) -> bool:
        """Adiciona um path no MediaMTX"""
        try:
            payload = {
                "source": rtsp_url,
                "sourceOnDemand": on_demand
            }
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/v3/config/paths/add/{path}",
                    json=payload,
                    auth=self.auth
                )
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Path {path} adicionado com sucesso")
                return True
            else:
                logger.error(f"❌ Erro ao adicionar path {path}: {response.status_code} - {response.text}")
                return False
                
        except httpx.TimeoutException:
            logger.error(f"⏱️ Timeout ao adicionar path {path}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar path {path}: {str(e)}")
            return False
    
    def remove_path(self, path: str) -> bool:
        """Remove um path do MediaMTX"""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.delete(
                    f"{self.base_url}/v3/config/paths/delete/{path}",
                    auth=self.auth
                )
            
            if response.status_code in [200, 204, 404]:
                logger.info(f"✅ Path {path} removido")
                return True
            else:
                logger.error(f"❌ Erro ao remover path {path}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao remover path {path}: {str(e)}")
            return False
    
    def get_path_status(self, path: str) -> Optional[Dict[str, Any]]:
        """Obtém status de um path"""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/v3/paths/get/{path}",
                    auth=self.auth
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter status do path {path}: {str(e)}")
            return None
