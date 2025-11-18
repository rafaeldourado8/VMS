# ai_detection/app/main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Optional
import base64
import os # <-- Adicionado

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
model_manager = ModelManager(models_dir=settings.MODELS_DIR) # Passa o diretório
detection_service = DetectionService(model_manager)
alert_service = AlertService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    logger.info("Iniciando serviço de IA...")
    # --- MUDANÇA AQUI ---
    # Carrega o modelo LPR customizado por defeito
    model_path = os.path.join(settings.MODELS_DIR, settings.DEFAULT_MODEL)
    await model_manager.load_custom_model(model_path)
    # ---------------------
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
    model_info = model_manager.get_current_model_info()
    return {
        "service": "VMS AI Detection Service",
        "version": "1.0.0",
        "status": "running",
        "model": model_info['name'] if model_info else "Nenhum"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica saúde do serviço"""
    model_info = model_manager.get_current_model_info()
    return {
        "status": "healthy",
        "model_loaded": model_info is not None,
        "current_model": model_info['name'] if model_info else "Nenhum",
        "device": model_info['device'] if model_info else "N/A",
        "active_detections": len(detection_service.detection_tasks)
    }

# --- MUDANÇA SIGNIFICATIVA AQUI ---
@app.websocket("/ws/detect/{camera_id}")
async def websocket_detection(websocket: WebSocket, camera_id: str):
    """
    WebSocket para INICIAR E PARAR a detecção.
    Os resultados da deteção são enviados via POST para o Django,
    não são enviados de volta por este WebSocket.
    
    Configuração inicial (JSON):
    {
        "rtsp_url": "rtsp://...",
        "confidence": 0.5,
        "classes": ["plate"],
        "fps": 10
    }
    """
    await websocket.accept()
    
    config = None
    try:
        # 1. Recebe configuração
        config_data = await websocket.receive_json()
        config = DetectionConfig(**config_data)
        
        logger.info(f"[{camera_id}] WebSocket: Recebida config, a iniciar stream...")
        
        # 2. Inicia o processamento em background
        await detection_service.start_stream_processing(camera_id, config)
        await websocket.send_json({"status": "processing_started", "camera_id": camera_id})

        # 3. Mantém o WebSocket aberto para sinal de paragem
        #    (ou podemos fechar, dependendo da sua lógica)
        while True:
            # Apenas esperamos que o cliente desconecte
            data = await websocket.receive_text()
            if data == "stop":
                logger.info(f"[{camera_id}] Recebido comando 'stop' via WebSocket.")
                break
                
    except WebSocketDisconnect:
        logger.info(f"Cliente desconectado: {camera_id}. A parar stream.")
    except Exception as e:
        logger.error(f"Erro no WebSocket {camera_id}: {str(e)}")
        await websocket.close(code=1011, reason=str(e))
    finally:
        # 4. Para o processamento quando o WebSocket fecha
        logger.info(f"A parar deteção para {camera_id} (limpeza do WebSocket).")
        await detection_service.stop_detection(camera_id)
# -------------------------------------

@app.post("/detect/frame", response_model=DetectionResult, tags=["Detection"])
async def detect_frame(
    camera_id: str,
    frame_base64: str,
    confidence: float = 0.5,
    classes: Optional[list] = None
):
    """
    Detecta objetos em um frame único
    (Ainda usa a lógica simulada do detection_service)
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

@app.get("/models/current", response_model=Optional[ModelInfo], tags=["Models"])
async def get_current_model():
    """Obtém informações do modelo atual"""
    return model_manager.get_current_model_info()

@app.post("/models/load/{model_name}", tags=["Models"])
async def load_model(model_name: str):
    """Carrega um modelo específico (genérico)"""
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