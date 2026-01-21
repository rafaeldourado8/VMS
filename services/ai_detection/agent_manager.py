import logging
import requests
import time
import cv2
from camera_agent import CameraAgent

logger = logging.getLogger(__name__)

class AgentManager:
    # Recebe os 3 modelos aqui
    def __init__(self, vehicle_model, custom_model, plate_model, ocr_model, backend_url, mediamtx_host, rabbitmq_producer=None):
        self.vehicle_model = vehicle_model
        self.custom_model = custom_model
        self.plate_model = plate_model
        self.ocr_model = ocr_model
        self.backend_url = backend_url
        self.mediamtx_host = mediamtx_host
        self.rabbitmq_producer = rabbitmq_producer
        self.active_agents = {}

    def start_camera(self, camera_id: int):
        if camera_id in self.active_agents: return
        
        rtsp_url = f"rtsp://{self.mediamtx_host}:8554/cam_{camera_id}"
        
        # Passa os 3 modelos para o agente
        agent = CameraAgent(
            camera_id=camera_id,
            rtsp_url=rtsp_url,
            vehicle_model=self.vehicle_model,
            custom_model=self.custom_model,
            plate_model=self.plate_model,
            ocr_model=self.ocr_model,
            backend_url=self.backend_url,
            rabbitmq_producer=self.rabbitmq_producer
        )
        agent.start()
        self.active_agents[camera_id] = agent
        logger.info(f" Camera {camera_id} iniciada com Triple-Core AI")

    def stop_camera(self, camera_id):
        if camera_id in self.active_agents:
            self.active_agents[camera_id].stop()
            del self.active_agents[camera_id]

    def load_cameras_from_backend(self):
        try:
            response = requests.get(f"{self.backend_url}/api/internal/cameras/", timeout=5)
            if response.status_code == 200:
                for cam in response.json():
                    if cam.get("ai_enabled", False):
                        self.start_camera(cam["id"])
        except: pass

    def stop_all(self):
        for cid in list(self.active_agents.keys()):
            self.stop_camera(cid)