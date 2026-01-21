import cv2
import logging
import time
import os
from datetime import datetime
from threading import Thread
from config.settings import settings
from core.motion_detector import MotionDetector
from core.vehicle_detector import VehicleDetector
from core.tracker import VehicleTracker
from core.quality_scorer import QualityScorer
from core.plate_detector import PlateDetector
from core.ocr_engine import OCREngine
from pipeline.consensus_engine import ConsensusEngine
from pipeline.dedup_cache import DedupCache
from pipeline.frame_extractor import FrameExtractor
from integration.rabbitmq_producer import RabbitMQProducer
from integration.mediamtx_client import MediaMTXClient
from api.control_api import ControlAPI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIDetectionService:
    def __init__(self):
        self.active_cameras = {}
        self.mediamtx = MediaMTXClient(base_url=settings.MEDIAMTX_URL)
        self.rabbitmq = RabbitMQProducer(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            user=settings.RABBITMQ_USER,
            password=settings.RABBITMQ_PASS
        )
        
        self.api = ControlAPI(port=settings.API_PORT)
        self.api.set_callbacks(self.start_camera, self.stop_camera)
        
        # Diretório para salvar recortes de teste
        self.detections_dir = "/app/detections"
        os.makedirs(self.detections_dir, exist_ok=True)
    
    def start_camera(self, camera_id: int, source_url: str = None) -> bool:
        """
        Inicia processamento de uma câmera
        """
        try:
            # 1. Resolve a URL de origem (WHEP ou RTSP)
            if not source_url:
                if settings.USE_WEBRTC:
                    # Pega a URL WHEP (http://mediamtx:8889/cam/whep)
                    source_url = self.mediamtx.get_webrtc_url(camera_id)
                    logger.info(f"Selected Protocol: WHEP/WebRTC for camera {camera_id}")
                else:
                    # Pega a URL RTSP (rtsp://mediamtx:8554/cam)
                    source_url = self.mediamtx.get_rtsp_url(camera_id)
                    logger.info(f"Selected Protocol: RTSP for camera {camera_id}")

            logger.info(f"Connecting to source: {source_url}")
            
            # 2. Instancia o Extrator (Atualizado para o novo FrameExtractor)
            # Nota: Removemos 'use_webrtc' pois a classe agora gerencia isso internamente ou via URL
            extractor = FrameExtractor(
                camera_id=camera_id, 
                source_url=source_url, 
                fps=settings.AI_FPS
            )
            
            # 3. Inicia a thread de captura (Asyncio loop interno se for WebRTC)
            extractor.start()
            
            # 4. Inicia a thread de processamento de IA
            thread = Thread(
                target=self._process_camera,
                args=(camera_id, extractor),
                daemon=True
            )
            thread.start()
            
            self.active_cameras[camera_id] = {
                'extractor': extractor,
                'thread': thread,
                'source_url': source_url
            }
            
            logger.info(f"Successfully started pipeline for camera {camera_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to start camera {camera_id}: {e}", exc_info=True)
            return False
    
    def stop_camera(self, camera_id: int) -> bool:
        if camera_id not in self.active_cameras:
            return False
        
        try:
            # O stop() do FrameExtractor agora limpa o loop asyncio corretamente
            self.active_cameras[camera_id]['extractor'].stop()
            
            # Removemos da lista para que o loop _process_camera encerre
            del self.active_cameras[camera_id]
            logger.info(f"Stopped pipeline for camera {camera_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop camera {camera_id}: {e}")
            return False
    
    def _process_camera(self, camera_id: int, extractor: FrameExtractor):
        """Loop principal de processamento de IA"""
        
        # Inicializa modelos (Carregados apenas uma vez por thread)
        motion_detector = MotionDetector(
            threshold=settings.MOTION_THRESHOLD,
            var_threshold=settings.MOG2_VAR_THRESHOLD,
            history=settings.MOG2_HISTORY
        )
        
        vehicle_detector = VehicleDetector(
            model_path=settings.VEHICLE_MODEL,
            confidence=settings.VEHICLE_CONFIDENCE
        )
        
        tracker = VehicleTracker(
            iou_threshold=settings.TRACKER_IOU_THRESHOLD,
            timeout=settings.TRACKER_TIMEOUT
        )
        
        quality_scorer = QualityScorer(
            blur_w=settings.QUALITY_WEIGHT_BLUR,
            angle_w=settings.QUALITY_WEIGHT_ANGLE,
            contrast_w=settings.QUALITY_WEIGHT_CONTRAST,
            size_w=settings.QUALITY_WEIGHT_SIZE
        )
        
        plate_detector = PlateDetector(
            model_path=settings.PLATE_MODEL,
            confidence=settings.PLATE_CONFIDENCE
        )
        
        ocr_engine = OCREngine(model=settings.OCR_MODEL)
        
        consensus_engine = ConsensusEngine(
            min_readings=settings.MIN_READINGS,
            consensus_threshold=settings.CONSENSUS_THRESHOLD,
            similarity_threshold=settings.SIMILARITY_THRESHOLD
        )
        
        dedup_cache = DedupCache(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            ttl=settings.DEDUP_TTL
        )
        
        logger.info(f"AI Models loaded for camera {camera_id}. Starting detection loop.")
        
        while camera_id in self.active_cameras:
            try:
                # 1. Obtém frame do extrator (Non-blocking)
                frame = extractor.get_frame()
                if frame is None:
                    time.sleep(0.01) # Pequena pausa para não fritar a CPU
                    continue
                
                # 2. Detecção de Movimento (Filtro Rápido)
                has_motion, motion_ratio = motion_detector.detect(frame)
                if not has_motion:
                    continue
                
                # logger.debug(f"Motion detected: {motion_ratio:.4f}")
                
                # 3. Detecção de Veículos
                vehicles = vehicle_detector.detect(frame)
                if not vehicles:
                    continue
                
                # 4. Rastreamento (Tracking)
                completed_tracks = tracker.update(vehicles, frame)
                
                # 5. Processa Tracks Completos (Veículo saiu de cena ou track estável)
                for track in completed_tracks:
                    if len(track.frames) < settings.MIN_READINGS:
                        continue
                    
                    # 6. Seleção dos Melhores Frames (Quality Score)
                    scored_frames = []
                    for frame_data, bbox in track.frames:
                        score = quality_scorer.score(frame_data, bbox)
                        scored_frames.append((score['final'], frame_data, bbox))
                    
                    # Ordena e pega os TOP X frames
                    scored_frames.sort(reverse=True, key=lambda x: x[0])
                    best_frames = scored_frames[:settings.MAX_READINGS]
                    
                    # 7. Detecção de Placa e OCR nos melhores frames
                    readings = []
                    best_plate_crop = None
                    
                    for _, frame_data, bbox in best_frames:
                        x1, y1, x2, y2 = bbox
                        vehicle_crop = frame_data[y1:y2, x1:x2]
                        
                        plates = plate_detector.detect(vehicle_crop)
                        if not plates:
                            continue
                        
                        # Guarda o melhor recorte para salvar depois
                        crops = [p['crop'] for p in plates]
                        if crops and best_plate_crop is None:
                            best_plate_crop = crops[0]
                        
                        # OCR
                        ocr_results = ocr_engine.recognize(crops)
                        readings.extend(ocr_results)
                    
                    if not readings:
                        continue
                    
                    # 8. Consenso (Votação)
                    result = consensus_engine.vote(readings)
                    if not result or result['confidence'] < settings.MIN_CONFIDENCE:
                        continue
                    
                    # 9. Deduplicação (Redis)
                    if dedup_cache.is_duplicate(camera_id, result['plate']):
                        logger.info(f"Ignored duplicate plate: {result['plate']}")
                        continue
                    
                    dedup_cache.add(camera_id, result['plate'])
                    
                    # 10. Salva Evidência (Crop)
                    if best_plate_crop is not None:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{result['plate']}_{timestamp}_cam{camera_id}.jpg"
                        filepath = os.path.join(self.detections_dir, filename)
                        cv2.imwrite(filepath, best_plate_crop)
                    
                    # 11. Envia Evento (RabbitMQ)
                    self.rabbitmq.send_detection(
                        camera_id=camera_id,
                        plate=result['plate'],
                        confidence=result['confidence'],
                        method=result['method'],
                        metadata={
                            'track_id': track.track_id,
                            'frames_analyzed': len(track.frames),
                            'votes': result['votes'],
                            'total_reads': result['total']
                        }
                    )
                    
                    logger.info(f"CONFIRMED DETECTION: {result['plate']} ({result['confidence']:.2f})")
                
                # Controle de loop
                time.sleep(0.005)
                
            except Exception as e:
                logger.error(f"Error in processing loop camera {camera_id}: {e}")
                time.sleep(1)
    
    def run(self):
        logger.info("Starting AI Detection Service v2.0 (WebRTC Enabled)")
        logger.info(f"Config: WebRTC={settings.USE_WEBRTC}, FPS={settings.AI_FPS}")
        
        # Inicia API de controle
        self.api.run()
        
        # Auto-start câmeras existentes
        self._auto_start_cameras()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Service shutting down...")
            for camera_id in list(self.active_cameras.keys()):
                self.stop_camera(camera_id)
            self.rabbitmq.close()
    
    def _auto_start_cameras(self):
        """Busca câmeras no backend e inicia"""
        try:
            import requests
            url = f"{settings.BACKEND_URL}/api/cameras/"
            logger.info(f"Fetching cameras from: {url}")
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                cameras = response.json()
                count = 0
                for camera in cameras:
                    if camera.get('ai_enabled'):
                        logger.info(f"Auto-starting camera {camera['id']}")
                        # Passa None no source_url para forçar a lógica WHEP/RTSP do start_camera
                        self.start_camera(camera['id'], None) 
                        count += 1
                logger.info(f"Auto-started {count} cameras")
            else:
                logger.warning(f"Backend returned {response.status_code}")
        except Exception as e:
            logger.warning(f"Could not auto-start cameras: {e}")

if __name__ == "__main__":
    service = AIDetectionService()
    service.run()