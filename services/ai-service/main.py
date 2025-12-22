import asyncio
import base64
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import uvicorn

from config import settings
from models import DetectionRequest, DetectionResponse, HealthResponse, Detection
from queue_manager import QueueManager
from worker import DetectionWorker

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

workers = []
queue_manager = QueueManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await queue_manager.connect()
    
    for i in range(settings.workers):
        worker = DetectionWorker()
        asyncio.create_task(worker.start())
        workers.append(worker)
    
    logger.info(f"Started {settings.workers} workers")
    yield
    
    for worker in workers:
        await worker.stop()
    await queue_manager.disconnect()

app = FastAPI(
    title="GT-Vision AI Service",
    version="1.0.0",
    lifespan=lifespan
)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/health", response_model=HealthResponse)
async def health():
    queue_size = await queue_manager.get_queue_size()
    
    total_processed = sum(w.stats["processed"] for w in workers)
    total_time = sum(w.stats["total_time"] for w in workers)
    avg_time = total_time / total_processed if total_processed > 0 else 0
    
    gpu_available = settings.enable_gpu
    
    return HealthResponse(
        status="healthy",
        queue_size=queue_size,
        processed_total=total_processed,
        avg_processing_time_ms=avg_time,
        gpu_available=gpu_available
    )

@app.post("/detect", response_model=DetectionResponse)
async def detect(request: DetectionRequest):
    try:
        image_bytes = base64.b64decode(request.image_base64)
        task_id = await queue_manager.enqueue(request.camera_id, image_bytes)
        
        for _ in range(50):
            result = await queue_manager.get_result(task_id)
            if result:
                return DetectionResponse(
                    detections=[Detection(**d, camera_id=request.camera_id) for d in result["detections"]],
                    processing_time_ms=result["processing_time_ms"]
                )
            await asyncio.sleep(0.1)
        
        raise HTTPException(status_code=408, detail="Processing timeout")
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect/async")
async def detect_async(request: DetectionRequest):
    try:
        image_bytes = base64.b64decode(request.image_base64)
        task_id = await queue_manager.enqueue(request.camera_id, image_bytes)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    result = await queue_manager.get_result(task_id)
    if result:
        return result
    raise HTTPException(status_code=404, detail="Result not found")

@app.post("/detect/upload")
async def detect_upload(camera_id: int, file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        task_id = await queue_manager.enqueue(camera_id, image_bytes)
        
        for _ in range(50):
            result = await queue_manager.get_result(task_id)
            if result:
                return result
            await asyncio.sleep(0.1)
        
        raise HTTPException(status_code=408, detail="Processing timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=1,
        log_level=settings.log_level.lower()
    )
