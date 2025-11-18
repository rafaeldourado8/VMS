import asyncio
import logging
import cv2
import httpx
import time
from datetime import datetime
from typing import Dict, Optional, List

from ..services.model_manager import ModelManager
from ..schemas import DetectionConfig, DetectionResult, Detection
from ..config import settings # Importa as configurações (para a API Key)

logger = logging.getLogger(__name__)

class DetectionService:
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        # Tarefas de deteção ativas (camera_id -> asyncio.Task)
        self.detection_tasks: Dict[str, asyncio.Task] = {}
        
        # Cliente HTTP síncrono para ser usado DENTRO da thread de bloqueio
        # Aponta para a variável correta do Django (definida no .env e docker-compose)
        self.http_client = httpx.Client(base_url=settings.django_api_url, timeout=5.0)
        logger.info(f"DetectionService initialized. Posting to {settings.django_api_url}")

    async def start_stream_processing(self, camera_id: str, config: DetectionConfig):
        """
        Inicia uma tarefa em background para processar o stream de vídeo.
        """
        if camera_id in self.detection_tasks:
            logger.warning(f"Processamento para {camera_id} já está em execução.")
            return

        logger.info(f"Iniciando processamento de stream para: {config.rtsp_url}")
        
        # Cria a tarefa em background
        # Usamos asyncio.to_thread para correr a função de bloqueio _run_detection_loop
        # noutra thread, para não bloquear o loop principal do FastAPI.
        task = asyncio.create_task(
            asyncio.to_thread(self._run_detection_loop, camera_id, config),
            name=f"detection_loop_{camera_id}"
        )
        self.detection_tasks[camera_id] = task
        logger.info(f"Tarefa de deteção para {camera_id} criada.")

    def _run_detection_loop(self, camera_id: str, config: DetectionConfig):
        """
        [FUNÇÃO DE BLOQUEIO]
        Este é o loop de trabalho real que roda na sua própria thread.
        Lê frames, chama a IA (modelo) e envia os dados para o Django.
        """
        
        model = self.model_manager.get_model()
        if not model:
            logger.error(f"[{camera_id}] Modelo não carregado. A parar a thread.")
            return

        cap = None
        is_running = True
        
        while is_running:
            try:
                # Verifica se a tarefa foi cancelada (pelo stop_detection)
                if camera_id not in self.detection_tasks:
                    is_running = False
                    continue

                if cap is None or not cap.isOpened():
                    logger.info(f"[{camera_id}] A abrir stream: {config.rtsp_url}")
                    cap = cv2.VideoCapture(config.rtsp_url)
                    if not cap.isOpened():
                        logger.error(f"[{camera_id}] Falha ao abrir stream. A tentar novamente em 5s...")
                        time.sleep(5)
                        continue
                
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"[{camera_id}] Frame vazio. A tentar reconectar...")
                    cap.release()
                    cap = None
                    time.sleep(1) # Evita loop de reconexão muito rápido
                    continue

                # --- CHAMADA REAL DO MODELO DE IA ---
                results = model.predict(
                    source=frame,
                    verbose=False,
                    conf=config.confidence,
                    classes=config.classes 
                )
                
                # O resultado (results) é uma lista, processamos o primeiro
                if results and results[0].boxes:
                    self._process_and_ingest_results(camera_id, results[0])

                # Controla o FPS (simples)
                time.sleep(1.0 / config.fps)

            except Exception as e:
                logger.error(f"[{camera_id}] Erro fatal no loop de deteção: {e}", exc_info=True)
                is_running = False # Termina o loop em caso de erro
            
        # Limpeza
        if cap:
            cap.release()
        logger.info(f"[{camera_id}] Loop de deteção terminado.")


    def _process_and_ingest_results(self, camera_id: str, result):
        """
        Processa os resultados do YOLO e envia para o Django.
        """
        # 'result.boxes' contém as deteções
        for box in result.boxes:
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = self.model_manager.model.names[class_id]
            
            # --- LÓGICA DE INGESTÃO (POST para o Django) ---
            # TODO: Extrair o TEXTO da matrícula se o seu modelo LPR fizer OCR.
            # Este exemplo envia a classe (ex: 'plate') e a confiança.
            
            plate_data_example = f"SIMUL-{class_name.upper()}" # Substitua isto
            
            payload = {
                "camera_id": camera_id,
                # --- CORREÇÃO 1 ---
                # O Serializer do Django espera 'plate', não 'plate_data'
                "plate": plate_data_example, 
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(), # Envia em formato ISO
                # Envia o tipo de veículo (o serializer aceita)
                "vehicle_type": class_name if class_name in ["car", "bus", "truck", "motorcycle"] else "unknown"
            }
            
            self._send_to_django(payload)

    def _send_to_django(self, payload: dict):
        """
        Envia os dados de deteção para o endpoint de ingestão do Django.
        (Corre dentro da thread de deteção)
        """
        try:
            # --- CORREÇÃO 2 ---
            # Adiciona o header 'X-API-Key' para autenticação no Django
            # (Exigido pela permission 'HasIngestAPIKey')
            headers = {
                "X-API-Key": settings.INGEST_API_KEY
            }
            
            # NOTA: Usamos o cliente síncrono 'self.http_client'
            response = self.http_client.post(
                url="/api/deteccoes/ingest/", # Endpoint do Django
                json=payload,
                headers=headers # Envia os headers
            )
            
            response.raise_for_status() # Lança erro para 4xx ou 5xx
            logger.debug(f"Ingestão bem-sucedida: {payload.get('plate')}")
        
        except httpx.HTTPStatusError as e:
             logger.error(f"Erro do Django ao ingerir dados: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Falha ao enviar POST para o Django (Ingestão): {e}")


    async def stop_detection(self, camera_id: str) -> bool:
        """Para uma tarefa de deteção em execução."""
        task = self.detection_tasks.pop(camera_id, None)
        if task:
            if not task.done():
                task.cancel() # Cancela a tarefa asyncio
                # A lógica dentro de _run_detection_loop vai detetar e parar
            logger.info(f"Parada deteção para {camera_id}")
            return True
        logger.warning(f"Nenhuma tarefa de deteção encontrada para parar em {camera_id}")
        return False

    async def cleanup(self):
        """Limpa todas as tarefas em execução."""
        logger.info("Limpando todas as tarefas de deteção...")
        task_ids = list(self.detection_tasks.keys())
        for camera_id in task_ids:
            await self.stop_detection(camera_id)
        
        self.detection_tasks.clear()
        self.http_client.close() # Fecha o cliente HTTP
        logger.info("Limpeza completa.")

    # A função 'detect_single_frame' foi mantida como estava (simulada)
    # Se precisar dela real, terá que implementar a lógica de descodificação
    # de base64 e chamada do 'model.predict' de forma similar.
    async def detect_single_frame(self, camera_id: str, frame_base64: str, confidence: float, classes: Optional[list]) -> DetectionResult:
        """Simula deteção num único frame."""
        logger.info(f"Processando frame único para {camera_id}")
        
        # TODO: Implementar lógica real se necessário
        # 1. Decodificar base64 para imagem cv2
        # 2. Chamar model.predict() na imagem
        # 3. Retornar DetectionResult
        
        detections = [
            Detection(
                bbox=[20, 20, 150, 150],
                confidence=confidence,
                class_name=classes[0] if classes else "simulated_object",
            )
        ]
        
        return DetectionResult(
            camera_id=camera_id,
            timestamp=datetime.now(),
            detections=detections,
        )