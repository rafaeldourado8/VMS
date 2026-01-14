# 🔗 Guia de Integração entre Módulos

## 📋 Visão Geral

Este documento descreve como integrar os 4 módulos implementados.

---

## 🔄 Integrações Necessárias

### 1. Cidades → Cameras
**Objetivo:** Validar limites ao criar câmera

```python
# cameras/application/use_cases/create_camera.py

class CreateCameraUseCase:
    def __init__(
        self,
        camera_repo: ICameraRepository,
        city_repo: ICityRepository  # ← Adicionar
    ):
        self._camera_repo = camera_repo
        self._city_repo = city_repo
    
    def execute(self, request: CreateCameraRequest) -> str:
        # Busca cidade
        city = self._city_repo.find_by_id(request.city_id)
        if not city:
            raise ValueError("City not found")
        
        # Valida limites da cidade
        current_count = self._camera_repo.count_by_city(city.id)
        if not city.can_add_camera(current_count):
            raise ValueError(f"Max cameras limit reached ({city.max_cameras})")
        
        # Cria câmera
        camera = Camera(...)
        
        if camera.is_lpr_enabled():
            lpr_count = self._camera_repo.count_lpr_by_city(city.id)
            if not city.can_add_lpr_camera(lpr_count):
                raise ValueError(f"Max LPR cameras limit reached ({city.max_lpr_cameras})")
        
        self._camera_repo.save(camera)
        return camera.id
```

---

### 2. Cameras → Streaming
**Objetivo:** Auto-iniciar stream ao ativar câmera

```python
# cameras/application/use_cases/activate_camera.py

class ActivateCameraUseCase:
    def __init__(
        self,
        camera_repo: ICameraRepository,
        start_stream_use_case: StartStreamUseCase  # ← Adicionar
    ):
        self._camera_repo = camera_repo
        self._start_stream = start_stream_use_case
    
    def execute(self, camera_id: str) -> None:
        camera = self._camera_repo.find_by_id(camera_id)
        if not camera:
            raise ValueError("Camera not found")
        
        # Ativa câmera
        camera.activate()
        self._camera_repo.save(camera)
        
        # Inicia stream automaticamente
        hls_url = self._start_stream.execute(
            camera_id=camera.id,
            stream_url=camera.stream_url
        )
```

---

### 3. Streaming → LPR
**Objetivo:** Processar frames apenas de câmeras LPR

```python
# streaming/application/services/frame_processor.py

class FrameProcessorService:
    def __init__(
        self,
        camera_repo: ICameraRepository,
        process_frame_use_case: ProcessFrameUseCase
    ):
        self._camera_repo = camera_repo
        self._process_frame = process_frame_use_case
    
    def process_stream(self, camera_id: str):
        camera = self._camera_repo.find_by_id(camera_id)
        
        # Apenas câmeras com LPR ativo
        if not camera.is_lpr_enabled():
            return
        
        while camera.is_active():
            frame = self._extract_frame(camera_id)
            
            # Processa frame (YOLO + OCR)
            self._process_frame.execute(ProcessFrameRequest(
                camera_id=camera.id,
                city_id=camera.city_id,
                frame=frame
            ))
            
            time.sleep(0.33)  # 3 FPS
```

---

### 4. LPR → Blacklist (Alertas)
**Objetivo:** Enviar alertas em tempo real

```python
# lpr/application/services/alert_service.py

class AlertService:
    def __init__(self, blacklist_repo: IBlacklistRepository):
        self._blacklist_repo = blacklist_repo
    
    def check_and_alert(self, detection: Detection):
        # Verifica blacklist
        entry = self._blacklist_repo.find_by_plate(
            detection.plate,
            detection.city_id
        )
        
        if entry and entry.matches(detection.plate):
            # Envia alerta
            self._send_alert(AlertCreatedEvent(
                detection_id=detection.id,
                plate=detection.plate,
                reason=entry.reason,
                camera_id=detection.camera_id,
                occurred_at=datetime.now()
            ))
```

---

## 🔌 Dependency Injection

### Container de Injeção

```python
# infrastructure/di/container.py

class Container:
    def __init__(self):
        # Repositories
        self._city_repo = DjangoCityRepository()
        self._camera_repo = DjangoCameraRepository()
        self._stream_repo = DjangoStreamRepository()
        self._detection_repo = DjangoDetectionRepository()
        self._blacklist_repo = DjangoBlacklistRepository()
        
        # Providers
        self._mediamtx_provider = MediaMTXProvider()
        self._yolo_provider = YOLODetectionProvider()
    
    def get_create_camera_use_case(self) -> CreateCameraUseCase:
        return CreateCameraUseCase(
            camera_repo=self._camera_repo,
            city_repo=self._city_repo
        )
    
    def get_activate_camera_use_case(self) -> ActivateCameraUseCase:
        return ActivateCameraUseCase(
            camera_repo=self._camera_repo,
            start_stream_use_case=self.get_start_stream_use_case()
        )
    
    def get_start_stream_use_case(self) -> StartStreamUseCase:
        return StartStreamUseCase(
            stream_repo=self._stream_repo,
            provider=self._mediamtx_provider
        )
    
    def get_process_frame_use_case(self) -> ProcessFrameUseCase:
        return ProcessFrameUseCase(
            detection_repo=self._detection_repo,
            blacklist_repo=self._blacklist_repo,
            provider=self._yolo_provider
        )
```

---

## 📡 Eventos de Domínio

### Event Bus

```python
# shared/infrastructure/event_bus.py

class EventBus:
    def __init__(self):
        self._handlers = {}
    
    def subscribe(self, event_type: type, handler: callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def publish(self, event):
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(event)
```

### Handlers

```python
# cameras/application/handlers/camera_activated_handler.py

class CameraActivatedHandler:
    def __init__(self, start_stream_use_case: StartStreamUseCase):
        self._start_stream = start_stream_use_case
    
    def handle(self, event: CameraActivatedEvent):
        # Auto-inicia stream
        camera = self._camera_repo.find_by_id(event.camera_id)
        self._start_stream.execute(
            camera_id=camera.id,
            stream_url=camera.stream_url
        )
```

---

## 🔧 Configuração

### Django Settings

```python
# config/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'vms_admin',
        'USER': 'vms_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    # DBs das cidades são criados dinamicamente
}

DATABASE_ROUTERS = [
    'cidades.infrastructure.django.router.MultiTenantRouter'
]

# Celery
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# MediaMTX
MEDIAMTX_BASE_URL = 'http://mediamtx:9997'
MEDIAMTX_HLS_URL = 'http://mediamtx:8888'
```

---

## 🚀 Ordem de Inicialização

### 1. Criar Cidade
```python
city_id = create_city_use_case.execute(CreateCityRequest(
    name='São Paulo',
    slug='sao_paulo',
    plan='basic'
))
```

### 2. Adicionar Câmera
```python
camera_id = create_camera_use_case.execute(CreateCameraRequest(
    name='Camera LPR 1',
    stream_url='rtsp://192.168.1.100/stream',
    city_id=city_id
))
# Resultado: type='rtsp', lpr_enabled=True (auto-detectado)
```

### 3. Ativar Câmera
```python
activate_camera_use_case.execute(camera_id)
# Resultado:
# - Camera.status = 'active'
# - Stream iniciado no MediaMTX
# - Recording iniciado (24/7)
# - LPR pipeline iniciado (se RTSP)
```

### 4. Detecção Automática
```python
# Frame processor (Celery task)
while camera.is_active() and camera.is_lpr_enabled():
    frame = extract_frame(camera_id)
    detections = process_frame_use_case.execute(ProcessFrameRequest(
        camera_id=camera_id,
        city_id=city_id,
        frame=frame
    ))
    
    for detection in detections:
        # Verifica blacklist
        # Envia alerta se necessário
        # Notifica via WebSocket
```

---

## ✅ Checklist de Integração

### Cidades → Cameras
- [ ] Injetar ICityRepository no CreateCameraUseCase
- [ ] Validar limites usando city.can_add_camera()
- [ ] Validar limites LPR usando city.can_add_lpr_camera()

### Cameras → Streaming
- [ ] Injetar StartStreamUseCase no ActivateCameraUseCase
- [ ] Auto-iniciar stream ao ativar câmera
- [ ] Auto-parar stream ao desativar câmera

### Streaming → LPR
- [ ] Criar FrameProcessorService
- [ ] Verificar camera.is_lpr_enabled() antes de processar
- [ ] Implementar Celery task para processamento assíncrono

### LPR → Blacklist
- [ ] Criar AlertService
- [ ] Verificar blacklist após cada detecção
- [ ] Implementar WebSocket para notificações real-time

---

## 🎯 Resultado Final

Após integração completa:

1. **Criar cidade** → DB criado automaticamente
2. **Adicionar câmera** → Tipo detectado pela URL
3. **Ativar câmera** → Stream + Recording + LPR (se RTSP)
4. **Detecção automática** → Placas detectadas em tempo real
5. **Alertas** → Blacklist verificada automaticamente
6. **Notificações** → WebSocket para frontend

**Sistema totalmente integrado e funcional!** 🚀
