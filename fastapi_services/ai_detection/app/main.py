# fastapi_services/ai_detection/app/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Optional
import base64

from .config import settings
from .services.detection_service import DetectionService
from .services.model_manager import ModelManager
from .services.alert_service import AlertService
from .schemas import DetectionConfig, DetectionResult, ModelInfo, AlertConfig

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Serviços globais
model_manager = ModelManager()
detection_service = DetectionService(model_manager)
alert_service = AlertService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    logger.info("Iniciando serviço de IA...")
    await model_manager.load_default_model()
    yield
    logger.info("Encerrando serviço de IA...")
    await detection_service.cleanup()

app = FastAPI(
    title="VMS AI Detection Service",
    version="1.0.0",
    description="Serviço de detecção de objetos com IA",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz"""
    return {
        "service": "VMS AI Detection Service",
        "version": "1.0.0",
        "status": "running",
        "model": model_manager.current_model_name
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica saúde do serviço"""
    return {
        "status": "healthy",
        "model_loaded": model_manager.model is not None,
        "current_model": model_manager.current_model_name,
        "device": model_manager.device,
        "active_detections": len(detection_service.detection_tasks)
    }

@app.websocket("/ws/detect/{camera_id}")
async def websocket_detection(websocket: WebSocket, camera_id: str):
    """
    WebSocket para detecção em tempo real
    
    Configuração inicial (JSON):
    {
        "rtsp_url": "rtsp://...",
        "confidence": 0.5,
        "classes": ["person", "car"],
        "alert_enabled": true
    }
    """
    await websocket.accept()
    
    try:
        # Recebe configuração
        config_data = await websocket.receive_json()
        config = DetectionConfig(**config_data)
        
        logger.info(f"Iniciando detecção para câmera {camera_id}")
        
        # Processa stream com detecção
        async for result in detection_service.process_stream(camera_id, config):
            try:
                # Envia resultado
                await websocket.send_json(result.dict())
                
                # Verifica alertas
                if config.alert_enabled:
                    alerts = alert_service.check_alerts(result, config)
                    if alerts:
                        await websocket.send_json({
                            "type": "alert",
                            "alerts": alerts
                        })
                        
            except Exception as e:
                logger.error(f"Erro ao enviar detecção: {str(e)}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"Cliente desconectado: {camera_id}")
    except Exception as e:
        logger.error(f"Erro no WebSocket: {str(e)}")
    finally:
        await detection_service.stop_detection(camera_id)

@app.post("/detect/frame", response_model=DetectionResult, tags=["Detection"])
async def detect_frame(
    camera_id: str,
    frame_base64: str,
    confidence: float = 0.5,
    classes: Optional[list] = None
):
    """
    Detecta objetos em um frame único
    
    Parâmetros:
    - camera_id: ID da câmera
    - frame_base64: Frame codificado em base64
    - confidence: Confiança mínima (0-1)
    - classes: Classes específicas para detectar
    """
    try:
        result = await detection_service.detect_single_frame(
            camera_id, frame_base64, confidence, classes
        )
        return result
    except Exception as e:
        logger.error(f"Erro ao processar frame: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect/upload", response_model=DetectionResult, tags=["Detection"])
async def detect_upload(
    file: UploadFile = File(...),
    confidence: float = 0.5,
    classes: Optional[list] = None
):
    """Detecta objetos em uma imagem enviada"""
    try:
        contents = await file.read()
        frame_base64 = base64.b64encode(contents).decode('utf-8')
        
        result = await detection_service.detect_single_frame(
            "upload", frame_base64, confidence, classes
        )
        return result
    except Exception as e:
        logger.error(f"Erro ao processar upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models", response_model=list[ModelInfo], tags=["Models"])
async def list_models():
    """Lista modelos disponíveis"""
    return model_manager.list_available_models()

@app.get("/models/current", response_model=ModelInfo, tags=["Models"])
async def get_current_model():
    """Obtém informações do modelo atual"""
    return model_manager.get_current_model_info()

@app.post("/models/load/{model_name}", tags=["Models"])
async def load_model(model_name: str):
    """Carrega um modelo específico"""
    success = await model_manager.load_model(model_name)
    
    if not success:
        raise HTTPException(status_code=400, detail="Falha ao carregar modelo")
    
    return {
        "message": "Modelo carregado com sucesso",
        "model": model_name,
        "device": model_manager.device
    }

@app.get("/detections/active", tags=["Detection"])
async def list_active_detections():
    """Lista detecções ativas"""
    return {
        "active_detections": list(detection_service.detection_tasks.keys()),
        "total": len(detection_service.detection_tasks)
    }

@app.post("/detections/{camera_id}/stop", tags=["Detection"])
async def stop_detection(camera_id: str):
    """Para detecção para uma câmera"""
    success = await detection_service.stop_detection(camera_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Detecção não encontrada")
    
    return {"message": "Detecção parada com sucesso", "camera_id": camera_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )