import asyncio
import base64
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import uvicorn

from config import settings
from models import (
    DetectionRequest, DetectionResponse, HealthResponse, 
    Detection, WebhookData
)
from queue_manager import QueueManager
from worker import DetectionWorker, StreamWorker
from api_client import APIClient

# Configuração de logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Variáveis globais
task_workers: List[DetectionWorker] = []
stream_workers: List[StreamWorker] = []
queue_manager = QueueManager()
api_client = APIClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    # Startup
    logger.info("=" * 60)
    logger.info("GT-Vision AI Service Starting...")
    logger.info("=" * 60)
    
    # Cria diretórios necessários
    for directory in [settings.captures_dir, settings.pending_training_dir, 
                      settings.received_webhooks_dir, settings.logs_dir]:
        os.makedirs(directory, exist_ok=True)
    
    # Conecta ao Redis
    await queue_manager.connect()
    logger.info("Connected to Redis")
    
    # Inicia Task Workers (processam fila)
    for i in range(settings.workers):
        worker = DetectionWorker(worker_id=i)
        asyncio.create_task(worker.start())
        task_workers.append(worker)
    
    logger.info(f"Started {settings.workers} task workers")
    
    # Inicia Stream Workers (RTSP) se habilitado
    if settings.rtsp_enabled:
        asyncio.create_task(manage_rtsp_streams())
        logger.info("RTSP stream management enabled")
    
    # Health check do backend
    if await api_client.check_health():
        logger.info("Backend connection verified")
    else:
        logger.warning("Backend not reachable - some features may not work")
    
    logger.info("=" * 60)
    logger.info("AI Service Ready!")
    logger.info(f"Task Workers: {settings.workers}")
    logger.info(f"RTSP Mode: {'Enabled' if settings.rtsp_enabled else 'Disabled'}")
    logger.info(f"LPR Model: {settings.ocr_model}")
    logger.info(f"Motion Detection: Enabled (threshold={settings.motion_threshold})")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Service...")
    
    # Para task workers
    for worker in task_workers:
        await worker.stop()
    
    # Para stream workers
    for worker in stream_workers:
        await worker.stop()
    
    await queue_manager.disconnect()
    await api_client.close()
    
    logger.info("AI Service stopped")

app = FastAPI(
    title="GT-Vision AI Service",
    version="2.0.0",
    description="Unified AI service with LPR, Motion Detection and Dual-Mode processing",
    lifespan=lifespan
)

# Monta Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# ============================================================================
# ENDPOINTS - TASK MODE (Redis Queue)
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint com estatísticas."""
    queue_size = await queue_manager.get_queue_size()
    
    total_processed = sum(w.stats["processed"] for w in task_workers)
    total_time = sum(w.stats["total_time"] for w in task_workers)
    avg_time = total_time / total_processed if total_processed > 0 else 0
    
    return HealthResponse(
        status="healthy",
        queue_size=queue_size,
        processed_total=total_processed,
        avg_processing_time_ms=round(avg_time, 2),
        gpu_available=settings.enable_gpu,
        active_workers=len(task_workers),
        active_streams=len(stream_workers)
    )

@app.post("/detect", response_model=DetectionResponse)
async def detect(request: DetectionRequest):
    """
    Processa uma imagem e retorna detecções (modo síncrono).
    Aguarda o resultado do processamento.
    """
    try:
        image_bytes = base64.b64decode(request.image_base64)
        task_id = await queue_manager.enqueue(request.camera_id, image_bytes)
        
        # Aguarda resultado (timeout 5s)
        for _ in range(50):
            result = await queue_manager.get_result(task_id)
            if result:
                return DetectionResponse(
                    detections=[Detection(**d) for d in result["detections"]],
                    processing_time_ms=result["processing_time_ms"],
                    task_id=task_id
                )
            await asyncio.sleep(0.1)
        
        raise HTTPException(status_code=408, detail="Processing timeout")
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect/async")
async def detect_async(request: DetectionRequest):
    """
    Enfileira uma imagem para processamento assíncrono.
    Retorna task_id para consulta posterior.
    """
    try:
        image_bytes = base64.b64decode(request.image_base64)
        task_id = await queue_manager.enqueue(request.camera_id, image_bytes)
        
        return {
            "task_id": task_id,
            "status": "queued",
            "message": f"Task queued for processing. Use /result/{task_id} to get results."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    """Obtém o resultado de uma tarefa processada."""
    result = await queue_manager.get_result(task_id)
    if result:
        return result
    raise HTTPException(status_code=404, detail="Result not found or expired")

@app.post("/detect/upload")
async def detect_upload(camera_id: int, file: UploadFile = File(...)):
    """Upload de arquivo de imagem para detecção."""
    try:
        image_bytes = await file.read()
        task_id = await queue_manager.enqueue(camera_id, image_bytes)
        
        # Aguarda resultado
        for _ in range(50):
            result = await queue_manager.get_result(task_id)
            if result:
                return result
            await asyncio.sleep(0.1)
        
        raise HTTPException(status_code=408, detail="Processing timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WEBHOOK ENDPOINT (LPR Cameras)
# ============================================================================

@app.post("/lpr-webhook")
async def lpr_webhook(request: Request):
    """
    Endpoint para receber webhooks de câmeras LPR externas.
    Salva o JSON recebido e processa a detecção.
    """
    try:
        data = await request.json()
        
        logger.info("=" * 60)
        logger.info("LPR Webhook Received")
        logger.info("=" * 60)
        
        # Salva JSON se configurado
        if settings.webhook_save_json:
            await save_webhook_json(data)
        
        # Processa webhook
        await process_webhook(data)
        
        return JSONResponse(
            content={"status": "received", "message": "Webhook processed successfully"},
            status_code=200
        )
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def save_webhook_json(data: dict):
    """Salva o JSON do webhook em arquivo."""
    try:
        plate = data.get("Plate", {}).get("PlateNumber", "UNKNOWN")
        timestamp = int(time.time())
        filename = f"{timestamp}_{plate}.json"
        filepath = os.path.join(settings.received_webhooks_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        logger.debug(f"Webhook JSON saved: {filepath}")
    except Exception as e:
        logger.error(f"Error saving webhook JSON: {e}")

async def process_webhook(data: dict):
    """Processa dados do webhook LPR."""
    try:
        plate_text = data.get("Plate", {}).get("PlateNumber")
        camera_id = data.get("Channel", 0)
        camera_name = data.get("DeviceName", f"LPR Camera {camera_id}")
        
        if not plate_text:
            logger.warning("Webhook without plate number")
            return
        
        logger.info(f"Plate from webhook: {plate_text} (Camera: {camera_name})")
        
        # Envia para backend
        await api_client.send_sighting(
            plate=plate_text,
            camera_id=camera_id,
            confidence=data.get("Plate", {}).get("Confidence"),
            additional_data={
                "device_name": camera_name,
                "source": "webhook"
            }
        )
    
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")

# ============================================================================
# RTSP STREAM MANAGEMENT
# ============================================================================

async def manage_rtsp_streams():
    """
    Gerencia streams RTSP continuamente.
    Busca câmeras do backend e inicia/para workers conforme necessário.
    """
    logger.info("RTSP stream manager started")
    
    while True:
        try:
            # Busca câmeras do backend
            cameras = await api_client.get_cameras()
            
            # Filtra apenas câmeras RTSP ativas
            rtsp_cameras = [cam for cam in cameras if cam.get("rtsp_url") and cam.get("active", True)]
            
            # IDs atuais
            current_ids = {cam["id"] for cam in rtsp_cameras}
            active_ids = {worker.camera_id for worker in stream_workers}
            
            # Remove workers de câmeras que não existem mais
            for worker in list(stream_workers):
                if worker.camera_id not in current_ids:
                    logger.info(f"Stopping stream worker for camera {worker.camera_id}")
                    await worker.stop()
                    stream_workers.remove(worker)
            
            # Adiciona workers para novas câmeras
            for camera in rtsp_cameras:
                if camera["id"] not in active_ids:
                    logger.info(f"Starting stream worker for camera {camera['id']}")
                    worker = StreamWorker(camera)
                    asyncio.create_task(worker.start())
                    stream_workers.append(worker)
            
            # Aguarda antes de verificar novamente
            await asyncio.sleep(60)
        
        except Exception as e:
            logger.error(f"RTSP manager error: {e}")
            await asyncio.sleep(30)

# ============================================================================
# STATS ENDPOINTS
# ============================================================================

@app.get("/stats/workers")
async def get_workers_stats():
    """Retorna estatísticas dos task workers."""
    return {
        "task_workers": [w.get_stats() for w in task_workers],
        "total_workers": len(task_workers)
    }

@app.get("/stats/streams")
async def get_streams_stats():
    """Retorna estatísticas dos stream workers."""
    return {
        "stream_workers": [w.get_stats() for w in stream_workers],
        "total_streams": len(stream_workers)
    }

@app.get("/stats/all")
async def get_all_stats():
    """Retorna todas as estatísticas."""
    queue_size = await queue_manager.get_queue_size()
    
    return {
        "queue_size": queue_size,
        "task_workers": [w.get_stats() for w in task_workers],
        "stream_workers": [w.get_stats() for w in stream_workers],
        "total_task_workers": len(task_workers),
        "total_stream_workers": len(stream_workers)
    }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=1,  # Deve ser 1 para manter estado compartilhado
        log_level=settings.log_level.lower()
    )
