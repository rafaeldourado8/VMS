"""
Gerenciador de câmeras - Inicia extração de frames automaticamente
"""

import asyncio
import logging
import requests
from ffmpeg_worker import FFmpegFrameExtractor
from database import DetectionDatabase

logger = logging.getLogger(__name__)

class CameraManager:
    def __init__(self, rabbitmq_url: str, backend_url: str = "http://backend:8000"):
        self.rabbitmq_url = rabbitmq_url
        self.backend_url = backend_url
        self.extractor = FFmpegFrameExtractor(rabbitmq_url)
        self.db = DetectionDatabase()
        self.active_cameras = {}
        
    async def load_cameras_from_backend(self):
        """Carrega câmeras ativas do backend Django"""
        try:
            response = requests.get(f"{self.backend_url}/api/cameras/", timeout=10)
            if response.status_code == 200:
                cameras = response.json()
                logger.info(f"📹 {len(cameras)} câmeras encontradas no backend")
                return cameras
            else:
                logger.error(f"❌ Erro carregando câmeras: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"❌ Erro conectando ao backend: {e}")
            return []
    
    def build_rtsp_url(self, camera_data: dict) -> str:
        """Constrói URL RTSP da câmera"""
        # Assume que as câmeras estão configuradas no MediaMTX
        camera_id = camera_data.get('id')
        return f"rtsp://mediamtx:8554/camera{camera_id}"
    
    async def start_camera_extraction(self, camera_data: dict):
        """Inicia extração de frames para uma câmera"""
        camera_id = camera_data.get('id')
        camera_name = camera_data.get('name', f'Camera {camera_id}')
        
        if camera_id in self.active_cameras:
            logger.info(f"📹 Câmera {camera_name} já está ativa")
            return
        
        rtsp_url = self.build_rtsp_url(camera_data)
        
        try:
            # Configura zona de detecção padrão se não existir
            zone_config = self.db.get_zone_config(camera_id)
            if not zone_config:
                default_zone = {
                    'camera_id': camera_id,
                    'p1': (100, 200),  # Ponto P1 (entrada)
                    'p2': (100, 600),  # Ponto P2 (saída)
                    'distance_meters': 20.0,  # Distância entre P1 e P2
                    'speed_limit_kmh': 60.0,  # Limite de velocidade
                    'fps': 25.0  # FPS da câmera
                }
                self.db.configure_zone(default_zone)
                logger.info(f"🎯 Zona padrão configurada para {camera_name}")
            
            # Inicia extração de frames (1 FPS para IA)
            self.extractor.start_extraction(camera_id, rtsp_url, fps=1)
            self.active_cameras[camera_id] = {
                'name': camera_name,
                'rtsp_url': rtsp_url,
                'active': True
            }
            
            logger.info(f"🎬 Extração iniciada: {camera_name} ({rtsp_url})")
            
        except Exception as e:
            logger.error(f"❌ Erro iniciando extração para {camera_name}: {e}")
    
    async def stop_camera_extraction(self, camera_id: int):
        """Para extração de frames para uma câmera"""
        if camera_id in self.active_cameras:
            self.extractor.stop_extraction(camera_id)
            del self.active_cameras[camera_id]
            logger.info(f"🛑 Extração parada: Camera {camera_id}")
    
    async def monitor_cameras(self):
        """Monitora câmeras e inicia/para extração conforme necessário"""
        while True:
            try:
                # Carrega câmeras do backend
                cameras = await self.load_cameras_from_backend()
                
                # Inicia extração para câmeras novas
                for camera in cameras:
                    camera_id = camera.get('id')
                    if camera_id and camera_id not in self.active_cameras:
                        await self.start_camera_extraction(camera)
                
                # Para extração para câmeras removidas
                active_ids = [cam.get('id') for cam in cameras if cam.get('id')]
                for camera_id in list(self.active_cameras.keys()):
                    if camera_id not in active_ids:
                        await self.stop_camera_extraction(camera_id)
                
                # Aguarda 30 segundos antes de verificar novamente
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Erro no monitor de câmeras: {e}")
                await asyncio.sleep(10)
    
    async def start(self):
        """Inicia o gerenciador de câmeras"""
        logger.info("🚀 Iniciando gerenciador de câmeras...")
        
        # Conecta ao RabbitMQ
        self.extractor.connect_rabbitmq()
        
        # Inicia monitoramento
        await self.monitor_cameras()

async def main():
    """Função principal para testar o gerenciador"""
    rabbitmq_url = 'amqp://gtvision_user:your-rabbitmq-password-here@rabbitmq_ai:5672/'
    
    manager = CameraManager(rabbitmq_url)
    await manager.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())