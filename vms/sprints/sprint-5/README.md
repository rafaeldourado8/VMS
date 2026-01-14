# 🎯 Sprint 5: Integração + FastAPI Assíncrono (7 dias)

## 📋 Objetivo

Integrar módulos e implementar FastAPI assíncrono para streaming e LPR.

---

## 🚀 Entregáveis

### Dia 1-2: Integração entre Módulos

#### Cidades → Cameras
```python
# cameras/application/use_cases/create_camera.py
class CreateCameraUseCase:
    def __init__(self, camera_repo, city_repo):
        self._camera_repo = camera_repo
        self._city_repo = city_repo
    
    def execute(self, request):
        city = self._city_repo.find_by_id(request.city_id)
        
        # Valida limites da cidade
        if not city.can_add_camera(current_count):
            raise MaxCamerasError()
        
        if camera.is_lpr_enabled():
            if not city.can_add_lpr_camera(lpr_count):
                raise MaxLPRCamerasError()
```

#### Cameras → Streaming
```python
# cameras/application/use_cases/activate_camera.py
class ActivateCameraUseCase:
    def __init__(self, camera_repo, start_stream_use_case):
        self._camera_repo = camera_repo
        self._start_stream = start_stream_use_case
    
    def execute(self, camera_id):
        camera.activate()
        
        # Auto-inicia stream
        hls_url = self._start_stream.execute(
            camera_id=camera.id,
            stream_url=camera.stream_url
        )
```

---

### Dia 3-4: FastAPI Assíncrono para Streaming

#### API de Streaming
```python
# streaming/presentation/fastapi/router.py
from fastapi import APIRouter, WebSocket
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/v1/streaming")

@router.post("/streams/{camera_id}/start")
async def start_stream(camera_id: str):
    """Inicia stream HLS"""
    use_case = container.get_start_stream_use_case()
    hls_url = await asyncio.to_thread(
        use_case.execute,
        camera_id=camera_id,
        stream_url=camera.stream_url
    )
    return {"hls_url": hls_url}

@router.get("/streams/{camera_id}/hls")
async def get_hls_stream(camera_id: str):
    """Retorna stream HLS"""
    stream = await stream_repo.find_by_camera_id(camera_id)
    return RedirectResponse(stream.hls_url)

@router.websocket("/streams/{camera_id}/ws")
async def stream_websocket(websocket: WebSocket, camera_id: str):
    """WebSocket para status do stream"""
    await websocket.accept()
    
    while True:
        stream = await stream_repo.find_by_camera_id(camera_id)
        await websocket.send_json({
            "status": stream.status,
            "viewers": stream.viewers
        })
        await asyncio.sleep(1)
```

#### Frame Extractor Assíncrono
```python
# streaming/infrastructure/frame_extractor.py
import asyncio
import cv2

class AsyncFrameExtractor:
    async def extract_frame(self, stream_url: str) -> np.ndarray:
        """Extrai frame de forma assíncrona"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._extract_frame_sync,
            stream_url
        )
    
    def _extract_frame_sync(self, stream_url: str) -> np.ndarray:
        cap = cv2.VideoCapture(stream_url)
        ret, frame = cap.read()
        cap.release()
        return frame if ret else None
```

---

### Dia 5-6: FastAPI Assíncrono para LPR

#### API de Detecção
```python
# lpr/presentation/fastapi/router.py
from fastapi import APIRouter, UploadFile, WebSocket

router = APIRouter(prefix="/api/v1/lpr")

@router.post("/detect")
async def detect_plate(file: UploadFile):
    """Detecta placa em imagem enviada"""
    contents = await file.read()
    frame = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
    
    use_case = container.get_process_frame_use_case()
    detections = await asyncio.to_thread(
        use_case.execute,
        ProcessFrameRequest(
            camera_id="manual",
            city_id="test",
            frame=frame
        )
    )
    
    return {"detections": [d.to_dict() for d in detections]}

@router.websocket("/detections/{camera_id}/ws")
async def detections_websocket(websocket: WebSocket, camera_id: str):
    """WebSocket para detecções em tempo real"""
    await websocket.accept()
    
    async for detection in detection_stream(camera_id):
        await websocket.send_json({
            "plate": detection.plate,
            "confidence": detection.confidence,
            "detected_at": detection.detected_at.isoformat()
        })
```

#### Pipeline Assíncrono
```python
# lpr/application/services/async_detection_pipeline.py
import asyncio

class AsyncDetectionPipeline:
    async def process_camera(self, camera_id: str):
        """Processa frames de uma câmera de forma assíncrona"""
        camera = await self._camera_repo.find_by_id(camera_id)
        
        if not camera.is_lpr_enabled():
            return
        
        while camera.is_active():
            # Extrai frame assíncrono
            frame = await self._frame_extractor.extract_frame(
                camera.stream_url
            )
            
            # Processa frame (YOLO + OCR)
            detections = await asyncio.to_thread(
                self._process_frame_use_case.execute,
                ProcessFrameRequest(
                    camera_id=camera.id,
                    city_id=camera.city_id,
                    frame=frame
                )
            )
            
            # Notifica via WebSocket
            for detection in detections:
                await self._notify_detection(detection)
            
            # 3 FPS (processa 1 a cada 3 frames)
            await asyncio.sleep(0.33)
```

---

### Dia 7: Dependency Injection + Testes

#### Container
```python
# infrastructure/di/container.py
class Container:
    def __init__(self):
        self._repos = {}
        self._providers = {}
        self._use_cases = {}
    
    def get_create_camera_use_case(self):
        return CreateCameraUseCase(
            camera_repo=self.get_camera_repo(),
            city_repo=self.get_city_repo()
        )
    
    def get_start_stream_use_case(self):
        return StartStreamUseCase(
            stream_repo=self.get_stream_repo(),
            provider=self.get_mediamtx_provider()
        )
```

#### Testes de Integração
```python
# tests/integration/test_camera_streaming_integration.py
async def test_activate_camera_starts_stream():
    # Arrange
    camera = await create_test_camera()
    
    # Act
    await activate_camera_use_case.execute(camera.id)
    
    # Assert
    stream = await stream_repo.find_by_camera_id(camera.id)
    assert stream.status == 'active'
    assert stream.hls_url is not None
```

---

## ✅ Checklist

### Integração
- [ ] Cidades → Cameras (validação de limites)
- [ ] Cameras → Streaming (auto-start)
- [ ] Streaming → LPR (frame processing)
- [ ] LPR → Blacklist (alertas)

### FastAPI Streaming
- [ ] POST /streams/{id}/start
- [ ] GET /streams/{id}/hls
- [ ] WebSocket /streams/{id}/ws
- [ ] AsyncFrameExtractor

### FastAPI LPR
- [ ] POST /detect (upload imagem)
- [ ] WebSocket /detections/{id}/ws
- [ ] AsyncDetectionPipeline

### Infraestrutura
- [ ] Dependency Injection Container
- [ ] Event Bus
- [ ] Testes de integração

---

## 🎯 Métricas de Sucesso

1. ✅ Todos os módulos integrados
2. ✅ FastAPI funcionando (async)
3. ✅ WebSocket real-time
4. ✅ 20 câmeras processando simultaneamente
5. ✅ Latência < 100ms

---

## 🚀 Próximo Sprint

**Sprint 6:** YOLO Real + Recording Service
