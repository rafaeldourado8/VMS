"""
Gerenciador de Agentes de Câmeras
"""
import logging
import requests
from camera_agent import CameraAgent

logger = logging.getLogger(__name__)

class AgentManager:
    def __init__(self, yolo_model, ocr_model, backend_url, mediamtx_host):
        self.yolo_model = yolo_model
        self.ocr_model = ocr_model
        self.backend_url = backend_url
        self.mediamtx_host = mediamtx_host
        self.active_agents = {}  # {camera_id: agent}
    
    def start_camera(self, camera_id: int):
        """Inicia agente para uma câmera"""
        if camera_id in self.active_agents:
            logger.info(f"Camera {camera_id} já está ativa")
            return
        
        # Busca info da câmera do backend
        rtsp_url = f"rtsp://{self.mediamtx_host}:8554/cam_{camera_id}"
        
        agent = CameraAgent(
            camera_id=camera_id,
            rtsp_url=rtsp_url,
            model_yolo=self.yolo_model,
            model_ocr=self.ocr_model,
            backend_url=self.backend_url
        )
        agent.start()
        self.active_agents[camera_id] = agent
        logger.info(f"✅ Camera {camera_id} iniciada")
    
    def stop_camera(self, camera_id: int):
        """Para agente de uma câmera"""
        if camera_id not in self.active_agents:
            logger.warning(f"Camera {camera_id} não está ativa")
            return
        
        agent = self.active_agents[camera_id]
        agent.stop()
        del self.active_agents[camera_id]
        logger.info(f"🛑 Camera {camera_id} parada")
    
    def load_cameras_from_backend(self):
        """Carrega câmeras ativas do backend"""
        try:
            response = requests.get(f"{self.backend_url}/api/internal/cameras/", timeout=5)
            if response.status_code == 200:
                cameras = response.json()
                for cam in cameras:
                    if cam.get("ai_enabled", False):
                        self.start_camera(cam["id"])
        except Exception as e:
            logger.warning(f"Não foi possível buscar câmeras do backend: {e}")
    
    def stop_all(self):
        """Para todos os agentes"""
        for camera_id in list(self.active_agents.keys()):
            self.stop_camera(camera_id)
