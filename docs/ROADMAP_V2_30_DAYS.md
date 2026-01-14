# 🚀 Roadmap VMS v2 - 30 Dias (DDD + SOLID + Clean Code)

> **Arquitetura:** DDD + SOLID + Complexidade Ciclomática < 10 + TDD

---

## 📐 Princípios Arquiteturais

### DDD (Domain-Driven Design)
```
src/
├── domain/              # Entidades, Value Objects, Agregados
├── application/         # Use Cases, DTOs, Interfaces
├── infrastructure/      # Implementações (DB, APIs, Cache)
└── presentation/        # Controllers, Serializers
```

### SOLID
- **S**ingle Responsibility: 1 classe = 1 responsabilidade
- **O**pen/Closed: Aberto para extensão, fechado para modificação
- **L**iskov Substitution: Subclasses substituíveis
- **I**nterface Segregation: Interfaces específicas
- **D**ependency Inversion: Dependa de abstrações

### Complexidade Ciclomática
- **Máximo:** 10 por função
- **Ideal:** < 5
- **Ferramenta:** `radon cc` (Python), `eslint-complexity` (JS)

---

## 📅 SEMANA 1: Core Domain + Infrastructure

### Dia 1: Setup + Domain Layer
**Objetivo:** Estrutura base + entidades de domínio

```python
# domain/entities/camera.py
from dataclasses import dataclass
from domain.value_objects import CameraId, StreamUrl, CameraStatus

@dataclass
class Camera:
    id: CameraId
    name: str
    stream_url: StreamUrl
    status: CameraStatus
    
    def activate(self) -> None:
        self.status = CameraStatus.ACTIVE
    
    def deactivate(self) -> None:
        self.status = CameraStatus.INACTIVE
```

**Entregáveis:**
- [ ] Camera (Entity)
- [ ] Detection (Entity)
- [ ] Recording (Entity)
- [ ] Value Objects (CameraId, PlateNumber, Confidence)
- [ ] Domain Events (CameraActivated, DetectionCreated)

**Métricas:**
- Complexidade: < 5
- Cobertura: 100%

---

### Dia 2: Repository Interfaces + Specifications
**Objetivo:** Contratos de persistência

```python
# domain/repositories/camera_repository.py
from abc import ABC, abstractmethod
from domain.entities import Camera
from domain.specifications import CameraSpecification

class ICameraRepository(ABC):
    @abstractmethod
    def save(self, camera: Camera) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, camera_id: CameraId) -> Camera | None:
        pass
    
    @abstractmethod
    def find_by_spec(self, spec: CameraSpecification) -> list[Camera]:
        pass
```

**Entregáveis:**
- [ ] ICameraRepository
- [ ] IDetectionRepository
- [ ] IRecordingRepository
- [ ] Specifications (ActiveCameras, DetectionsByDateRange)

---

### Dia 3: Use Cases (Application Layer)
**Objetivo:** Casos de uso isolados

```python
# application/use_cases/activate_camera.py
from dataclasses import dataclass
from domain.repositories import ICameraRepository
from domain.value_objects import CameraId

@dataclass
class ActivateCameraRequest:
    camera_id: str

class ActivateCameraUseCase:
    def __init__(self, camera_repo: ICameraRepository):
        self._repo = camera_repo
    
    def execute(self, request: ActivateCameraRequest) -> None:
        camera_id = CameraId(request.camera_id)
        camera = self._repo.find_by_id(camera_id)
        
        if not camera:
            raise CameraNotFoundError(camera_id)
        
        camera.activate()
        self._repo.save(camera)
```

**Entregáveis:**
- [ ] ActivateCamera
- [ ] CreateDetection
- [ ] StartRecording
- [ ] StopRecording
- [ ] SearchDetections

**Complexidade:** < 5 por use case

---

### Dia 4: Infrastructure - PostgreSQL
**Objetivo:** Implementação de repositórios

```python
# infrastructure/persistence/postgres/camera_repository.py
from domain.repositories import ICameraRepository
from domain.entities import Camera
from infrastructure.persistence.models import CameraModel

class PostgresCameraRepository(ICameraRepository):
    def save(self, camera: Camera) -> None:
        model = self._to_model(camera)
        model.save()
    
    def find_by_id(self, camera_id: CameraId) -> Camera | None:
        try:
            model = CameraModel.objects.get(id=camera_id.value)
            return self._to_entity(model)
        except CameraModel.DoesNotExist:
            return None
    
    def _to_entity(self, model: CameraModel) -> Camera:
        # Mapper logic
        pass
    
    def _to_model(self, entity: Camera) -> CameraModel:
        # Mapper logic
        pass
```

**Entregáveis:**
- [ ] PostgresCameraRepository
- [ ] PostgresDetectionRepository
- [ ] PostgresRecordingRepository
- [ ] Mappers (Model ↔ Entity)
- [ ] Migrations

---

### Dia 5: Infrastructure - Redis Cache
**Objetivo:** Cache layer com decorator pattern

```python
# infrastructure/cache/cached_camera_repository.py
from functools import wraps
from domain.repositories import ICameraRepository

class CachedCameraRepository(ICameraRepository):
    def __init__(self, repo: ICameraRepository, cache: ICache):
        self._repo = repo
        self._cache = cache
    
    def find_by_id(self, camera_id: CameraId) -> Camera | None:
        cache_key = f"camera:{camera_id.value}"
        
        # Try cache first
        cached = self._cache.get(cache_key)
        if cached:
            return self._deserialize(cached)
        
        # Fallback to repository
        camera = self._repo.find_by_id(camera_id)
        if camera:
            self._cache.set(cache_key, self._serialize(camera), ttl=300)
        
        return camera
```

**Entregáveis:**
- [ ] ICache interface
- [ ] RedisCache implementation
- [ ] CachedCameraRepository (Decorator)
- [ ] Cache invalidation strategy

---

### Dia 6: API Layer (Presentation)
**Objetivo:** Controllers REST

```python
# presentation/api/v1/cameras/views.py
from rest_framework.views import APIView
from application.use_cases import ActivateCameraUseCase

class ActivateCameraView(APIView):
    def __init__(self, use_case: ActivateCameraUseCase):
        self._use_case = use_case
    
    def post(self, request, camera_id):
        try:
            req = ActivateCameraRequest(camera_id=camera_id)
            self._use_case.execute(req)
            return Response(status=200)
        except CameraNotFoundError:
            return Response(status=404)
        except Exception as e:
            return Response(status=500)
```

**Entregáveis:**
- [ ] CameraViewSet (CRUD)
- [ ] DetectionViewSet (List, Filter)
- [ ] RecordingViewSet (CRUD)
- [ ] Dependency Injection container
- [ ] OpenAPI docs

---

### Dia 7: Tests + Refactor
**Objetivo:** 100% cobertura + refatoração

```python
# tests/unit/use_cases/test_activate_camera.py
import pytest
from application.use_cases import ActivateCameraUseCase
from tests.builders import CameraBuilder

def test_activate_camera_success():
    # Arrange
    camera = CameraBuilder().inactive().build()
    repo = InMemoryCameraRepository([camera])
    use_case = ActivateCameraUseCase(repo)
    
    # Act
    use_case.execute(ActivateCameraRequest(camera.id.value))
    
    # Assert
    saved_camera = repo.find_by_id(camera.id)
    assert saved_camera.status == CameraStatus.ACTIVE
```

**Entregáveis:**
- [ ] Unit tests (domain + application)
- [ ] Integration tests (infrastructure)
- [ ] E2E tests (API)
- [ ] Cobertura > 90%
- [ ] Complexidade < 10

---

## 📅 SEMANA 2: Streaming + Detection

### Dia 8: Streaming Domain
**Objetivo:** Agregado de Streaming

```python
# domain/aggregates/stream.py
from dataclasses import dataclass
from domain.entities import Camera
from domain.value_objects import StreamUrl, StreamStatus

@dataclass
class Stream:
    camera: Camera
    url: StreamUrl
    status: StreamStatus
    viewers: int = 0
    
    def start(self) -> None:
        if not self.camera.is_active():
            raise CameraNotActiveError()
        self.status = StreamStatus.LIVE
    
    def stop(self) -> None:
        self.status = StreamStatus.STOPPED
    
    def add_viewer(self) -> None:
        self.viewers += 1
    
    def remove_viewer(self) -> None:
        self.viewers = max(0, self.viewers - 1)
```

**Entregáveis:**
- [ ] Stream (Aggregate)
- [ ] StreamService (Domain Service)
- [ ] IStreamingProvider interface

---

### Dia 9: MediaMTX Integration
**Objetivo:** Adapter para MediaMTX

```python
# infrastructure/streaming/mediamtx_provider.py
from domain.services import IStreamingProvider
from domain.value_objects import StreamUrl

class MediaMTXProvider(IStreamingProvider):
    def __init__(self, api_client: MediaMTXClient):
        self._client = api_client
    
    def create_stream(self, camera_id: str, rtsp_url: str) -> StreamUrl:
        path = f"camera_{camera_id}"
        self._client.add_path(path, rtsp_url)
        hls_url = f"{self._client.base_url}/{path}/index.m3u8"
        return StreamUrl(hls_url)
    
    def delete_stream(self, camera_id: str) -> None:
        path = f"camera_{camera_id}"
        self._client.remove_path(path)
```

**Entregáveis:**
- [ ] MediaMTXProvider
- [ ] MediaMTXClient (HTTP wrapper)
- [ ] StartStreamUseCase
- [ ] StopStreamUseCase

---

### Dia 10: Detection Domain
**Objetivo:** Agregado de Detecção

```python
# domain/aggregates/detection.py
from dataclasses import dataclass
from domain.entities import Camera
from domain.value_objects import PlateNumber, Confidence, BoundingBox

@dataclass
class Detection:
    camera: Camera
    plate: PlateNumber
    confidence: Confidence
    bbox: BoundingBox
    timestamp: datetime
    
    def is_high_confidence(self) -> bool:
        return self.confidence.value >= 0.9
    
    def is_blacklisted(self, blacklist: set[PlateNumber]) -> bool:
        return self.plate in blacklist
```

**Entregáveis:**
- [ ] Detection (Aggregate)
- [ ] DetectionService (Domain Service)
- [ ] IDetectionProvider interface

---

### Dia 11: YOLO + OCR Integration
**Objetivo:** Adapter para IA

```python
# infrastructure/ai/yolo_detection_provider.py
from domain.services import IDetectionProvider
from domain.aggregates import Detection

class YOLODetectionProvider(IDetectionProvider):
    def __init__(self, model: YOLOModel, ocr: OCREngine):
        self._model = model
        self._ocr = ocr
    
    def detect(self, frame: np.ndarray, camera: Camera) -> list[Detection]:
        # YOLO detection
        results = self._model.predict(frame)
        
        detections = []
        for result in results:
            if result.confidence < 0.75:
                continue
            
            # OCR on plate region
            plate_img = self._crop_plate(frame, result.bbox)
            plate_text = self._ocr.read(plate_img)
            
            detection = Detection(
                camera=camera,
                plate=PlateNumber(plate_text),
                confidence=Confidence(result.confidence),
                bbox=BoundingBox.from_yolo(result.bbox),
                timestamp=datetime.now()
            )
            detections.append(detection)
        
        return detections
```

**Entregáveis:**
- [ ] YOLODetectionProvider
- [ ] OCREngine wrapper
- [ ] ProcessFrameUseCase
- [ ] Frame queue (Celery)

---

### Dia 12: Detection Pipeline
**Objetivo:** Pipeline assíncrono

```python
# application/services/detection_pipeline.py
from celery import Task
from application.use_cases import ProcessFrameUseCase

class DetectionPipeline:
    def __init__(self, use_case: ProcessFrameUseCase):
        self._use_case = use_case
    
    def process_camera(self, camera_id: str) -> None:
        # Get frame from stream
        frame = self._get_frame(camera_id)
        
        # Process async
        process_frame_task.delay(camera_id, frame)

@celery_app.task
def process_frame_task(camera_id: str, frame: bytes):
    # Dependency injection
    use_case = container.resolve(ProcessFrameUseCase)
    use_case.execute(ProcessFrameRequest(camera_id, frame))
```

**Entregáveis:**
- [ ] DetectionPipeline
- [ ] Celery tasks
- [ ] Frame extraction service
- [ ] Error handling + retry

---

### Dia 13: WebSocket Notifications
**Objetivo:** Real-time updates

```python
# infrastructure/websocket/detection_notifier.py
from channels.layers import get_channel_layer
from domain.events import DetectionCreatedEvent

class WebSocketDetectionNotifier:
    def __init__(self):
        self._channel_layer = get_channel_layer()
    
    async def notify(self, event: DetectionCreatedEvent) -> None:
        await self._channel_layer.group_send(
            f"camera_{event.camera_id}",
            {
                "type": "detection.created",
                "detection": self._serialize(event.detection)
            }
        )
```

**Entregáveis:**
- [ ] WebSocket consumer
- [ ] Event handlers
- [ ] Real-time detection feed

---

### Dia 14: Tests + Refactor
**Objetivo:** Testes de integração

**Entregáveis:**
- [ ] Integration tests (Streaming + Detection)
- [ ] Performance tests (1000 frames/s)
- [ ] Load tests (20 câmeras simultâneas)
- [ ] Refatoração

---

## 📅 SEMANA 3: Frontend + UX

### Dia 15: Frontend Architecture
**Objetivo:** Estrutura React com Clean Architecture

```typescript
// src/domain/entities/Camera.ts
export class Camera {
  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly streamUrl: string,
    public status: CameraStatus
  ) {}
  
  isActive(): boolean {
    return this.status === CameraStatus.ACTIVE;
  }
}

// src/application/use-cases/GetCamerasUseCase.ts
export class GetCamerasUseCase {
  constructor(private repo: ICameraRepository) {}
  
  async execute(): Promise<Camera[]> {
    return await this.repo.findAll();
  }
}

// src/infrastructure/repositories/ApiCameraRepository.ts
export class ApiCameraRepository implements ICameraRepository {
  async findAll(): Promise<Camera[]> {
    const response = await api.get('/cameras');
    return response.data.map(dto => this.toEntity(dto));
  }
}
```

**Entregáveis:**
- [ ] Domain layer (entities, interfaces)
- [ ] Application layer (use cases)
- [ ] Infrastructure layer (API, cache)
- [ ] Presentation layer (components)

---

### Dia 16: Camera Grid Component
**Objetivo:** Grid responsivo com lazy loading

```typescript
// src/presentation/components/CameraGrid.tsx
export const CameraGrid: FC = () => {
  const { cameras, isLoading } = useGetCameras();
  const { ref, inView } = useInView();
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {cameras.map(camera => (
        <CameraCard
          key={camera.id}
          camera={camera}
          lazy={!inView}
        />
      ))}
      <div ref={ref} />
    </div>
  );
};
```

**Entregáveis:**
- [ ] CameraGrid
- [ ] CameraCard
- [ ] Lazy loading
- [ ] Pagination (10/página)

---

### Dia 17: Video Player Component
**Objetivo:** HLS player com cache

```typescript
// src/presentation/components/VideoPlayer.tsx
export const VideoPlayer: FC<Props> = ({ streamUrl, cameraId }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [useThumbnail, setUseThumbnail] = useState(true);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setUseThumbnail(false);
      initHLS(videoRef.current, streamUrl);
    }, 10000); // 10s cache
    
    return () => clearTimeout(timer);
  }, [streamUrl]);
  
  if (useThumbnail) {
    return <Thumbnail cameraId={cameraId} />;
  }
  
  return <video ref={videoRef} autoPlay muted />;
};
```

**Entregáveis:**
- [ ] VideoPlayer (HLS.js)
- [ ] Thumbnail cache
- [ ] Error handling
- [ ] Loading states

---

### Dia 18: Detection List Component
**Objetivo:** Lista com filtros

```typescript
// src/presentation/components/DetectionList.tsx
export const DetectionList: FC = () => {
  const [filters, setFilters] = useState<DetectionFilters>({});
  const { detections, isLoading } = useGetDetections(filters);
  
  return (
    <div>
      <DetectionFilters onChange={setFilters} />
      <Table>
        {detections.map(detection => (
          <DetectionRow key={detection.id} detection={detection} />
        ))}
      </Table>
    </div>
  );
};
```

**Entregáveis:**
- [ ] DetectionList
- [ ] DetectionFilters
- [ ] DetectionRow
- [ ] Export (CSV, Excel)

---

### Dia 19: Real-time Updates
**Objetivo:** WebSocket integration

```typescript
// src/infrastructure/websocket/DetectionWebSocket.ts
export class DetectionWebSocket {
  private ws: WebSocket;
  
  connect(cameraId: string, onDetection: (d: Detection) => void): void {
    this.ws = new WebSocket(`ws://api/cameras/${cameraId}/detections`);
    
    this.ws.onmessage = (event) => {
      const detection = JSON.parse(event.data);
      onDetection(detection);
    };
  }
}

// src/presentation/hooks/useRealtimeDetections.ts
export const useRealtimeDetections = (cameraId: string) => {
  const [detections, setDetections] = useState<Detection[]>([]);
  
  useEffect(() => {
    const ws = new DetectionWebSocket();
    ws.connect(cameraId, (detection) => {
      setDetections(prev => [detection, ...prev]);
    });
    
    return () => ws.disconnect();
  }, [cameraId]);
  
  return detections;
};
```

**Entregáveis:**
- [ ] WebSocket client
- [ ] Real-time hooks
- [ ] Toast notifications
- [ ] Sound alerts

---

### Dia 20: State Management
**Objetivo:** Zustand stores

```typescript
// src/presentation/stores/cameraStore.ts
export const useCameraStore = create<CameraStore>((set, get) => ({
  cameras: [],
  selectedCamera: null,
  
  fetchCameras: async () => {
    const useCase = container.resolve(GetCamerasUseCase);
    const cameras = await useCase.execute();
    set({ cameras });
  },
  
  selectCamera: (id: string) => {
    const camera = get().cameras.find(c => c.id === id);
    set({ selectedCamera: camera });
  }
}));
```

**Entregáveis:**
- [ ] cameraStore
- [ ] detectionStore
- [ ] authStore
- [ ] Persistence (localStorage)

---

### Dia 21: Tests + Refactor
**Objetivo:** Testes frontend

```typescript
// src/presentation/components/__tests__/CameraGrid.test.tsx
describe('CameraGrid', () => {
  it('should render cameras', () => {
    const cameras = [CameraBuilder.build()];
    render(<CameraGrid cameras={cameras} />);
    
    expect(screen.getByText(cameras[0].name)).toBeInTheDocument();
  });
  
  it('should lazy load cameras', () => {
    // Test intersection observer
  });
});
```

**Entregáveis:**
- [ ] Component tests (React Testing Library)
- [ ] Hook tests
- [ ] E2E tests (Playwright)
- [ ] Cobertura > 80%

---

## 📅 SEMANA 4: Recording + Polish

### Dia 22: Recording Domain
**Objetivo:** Agregado de Gravação

```python
# domain/aggregates/recording.py
@dataclass
class Recording:
    camera: Camera
    start_time: datetime
    end_time: datetime | None
    file_path: str
    status: RecordingStatus
    
    def stop(self) -> None:
        if self.status != RecordingStatus.RECORDING:
            raise InvalidRecordingStateError()
        
        self.end_time = datetime.now()
        self.status = RecordingStatus.COMPLETED
    
    def duration(self) -> timedelta:
        end = self.end_time or datetime.now()
        return end - self.start_time
```

**Entregáveis:**
- [ ] Recording (Aggregate)
- [ ] RecordingService
- [ ] IStorageProvider interface

---

### Dia 23: Recording Service
**Objetivo:** Gravação contínua

```python
# infrastructure/recording/ffmpeg_recorder.py
class FFmpegRecorder(IRecorder):
    def start_recording(self, camera: Camera) -> Recording:
        output_path = self._generate_path(camera)
        
        process = subprocess.Popen([
            'ffmpeg',
            '-i', camera.stream_url.value,
            '-c', 'copy',
            '-f', 'segment',
            '-segment_time', '3600',  # 1h segments
            '-reset_timestamps', '1',
            output_path
        ])
        
        return Recording(
            camera=camera,
            start_time=datetime.now(),
            file_path=output_path,
            status=RecordingStatus.RECORDING
        )
```

**Entregáveis:**
- [ ] FFmpegRecorder
- [ ] Segmented recording (1h chunks)
- [ ] Cyclic deletion (7/15/30 dias)
- [ ] Health monitoring

---

### Dia 24: Playback API
**Objetivo:** Busca e reprodução

```python
# application/use_cases/search_recordings.py
@dataclass
class SearchRecordingsRequest:
    camera_id: str
    start_date: datetime
    end_date: datetime

class SearchRecordingsUseCase:
    def execute(self, req: SearchRecordingsRequest) -> list[Recording]:
        spec = RecordingsByDateRangeSpec(
            camera_id=CameraId(req.camera_id),
            start=req.start_date,
            end=req.end_date
        )
        
        return self._repo.find_by_spec(spec)
```

**Entregáveis:**
- [ ] SearchRecordings
- [ ] GetRecordingSegment
- [ ] CreateClip
- [ ] Timeline API

---

### Dia 25: Timeline Component
**Objetivo:** Timeline interativa

```typescript
// src/presentation/components/Timeline.tsx
export const Timeline: FC<Props> = ({ recordings, onSeek }) => {
  const [position, setPosition] = useState(0);
  
  const handleClick = (e: MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = x / rect.width;
    const timestamp = calculateTimestamp(percentage, recordings);
    
    onSeek(timestamp);
  };
  
  return (
    <div className="timeline" onClick={handleClick}>
      {recordings.map(rec => (
        <TimelineSegment key={rec.id} recording={rec} />
      ))}
      <TimelineMarker position={position} />
    </div>
  );
};
```

**Entregáveis:**
- [ ] Timeline component
- [ ] Seek functionality
- [ ] Segment visualization
- [ ] Detection markers

---

### Dia 26: Clip System
**Objetivo:** Criar clipes permanentes

```python
# application/use_cases/create_clip.py
@dataclass
class CreateClipRequest:
    recording_id: str
    start_time: datetime
    end_time: datetime
    name: str

class CreateClipUseCase:
    def execute(self, req: CreateClipRequest) -> Clip:
        recording = self._recording_repo.find_by_id(req.recording_id)
        
        clip = Clip.create(
            recording=recording,
            start=req.start_time,
            end=req.end_time,
            name=req.name
        )
        
        # Extract clip async
        extract_clip_task.delay(clip.id)
        
        return self._clip_repo.save(clip)
```

**Entregáveis:**
- [ ] CreateClip
- [ ] DeleteClip
- [ ] ListClips
- [ ] FFmpeg extraction

---

### Dia 27: Performance Optimization
**Objetivo:** Otimizações finais

**Backend:**
- [ ] Query optimization (N+1, indexes)
- [ ] Connection pooling
- [ ] Cache warming
- [ ] Async tasks

**Frontend:**
- [ ] Code splitting
- [ ] Image optimization
- [ ] Bundle size < 500KB
- [ ] Lighthouse score > 90

---

### Dia 28: Documentation
**Objetivo:** Documentação completa

**Entregáveis:**
- [ ] API docs (OpenAPI/Swagger)
- [ ] Architecture docs (C4 model)
- [ ] Setup guide (README)
- [ ] Deployment guide (Docker)
- [ ] User manual

---

### Dia 29: Security + Monitoring
**Objetivo:** Segurança e observabilidade

**Security:**
- [ ] JWT authentication
- [ ] RBAC (Role-Based Access Control)
- [ ] Rate limiting
- [ ] Input validation
- [ ] SQL injection prevention

**Monitoring:**
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Error tracking (Sentry)
- [ ] Logging (ELK)

---

### Dia 30: Deploy + Demo
**Objetivo:** Deploy em produção

**Entregáveis:**
- [ ] Docker Compose production
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Backup strategy
- [ ] Rollback plan
- [ ] Demo video
- [ ] Pitch deck

---

## 📊 Métricas de Qualidade

### Complexidade Ciclomática
```bash
# Python
radon cc src/ -a -nb

# Target: Average < 5, Max < 10
```

### Cobertura de Testes
```bash
# Backend
pytest --cov=src --cov-report=html

# Frontend
npm run test:coverage

# Target: > 90%
```

### SOLID Compliance
```python
# Checklist por classe:
- [ ] Single Responsibility (1 motivo para mudar)
- [ ] Open/Closed (extensível sem modificar)
- [ ] Liskov Substitution (subclasses substituíveis)
- [ ] Interface Segregation (interfaces específicas)
- [ ] Dependency Inversion (depende de abstrações)
```

### Performance
```
- API Response Time: < 200ms (P95)
- Frontend Load Time: < 3s
- Detection Latency: < 500ms
- Stream Start Time: < 2s
```

---

## 🛠️ Ferramentas

### Backend
- **Framework:** Django 5.1
- **DDD:** python-ddd
- **Tests:** pytest, pytest-cov
- **Quality:** radon, pylint, black
- **Async:** Celery + RabbitMQ

### Frontend
- **Framework:** React 18 + Vite
- **State:** Zustand
- **Tests:** Vitest, React Testing Library, Playwright
- **Quality:** ESLint, Prettier
- **Types:** TypeScript strict mode

### DevOps
- **Container:** Docker + Docker Compose
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus + Grafana
- **Logs:** ELK Stack

---

## 📈 Checklist Final

### Arquitetura
- [ ] DDD layers implementadas
- [ ] SOLID principles aplicados
- [ ] Complexidade < 10
- [ ] Dependency Injection
- [ ] Event-Driven Architecture

### Qualidade
- [ ] Cobertura > 90%
- [ ] Sem code smells
- [ ] Documentação completa
- [ ] Performance otimizada
- [ ] Security hardened

### Funcionalidades
- [ ] Streaming HLS
- [ ] Detecção LPR
- [ ] Gravação contínua
- [ ] Playback + Timeline
- [ ] Clipes permanentes
- [ ] Real-time notifications

### Deploy
- [ ] Docker Compose
- [ ] CI/CD pipeline
- [ ] Monitoring
- [ ] Backup
- [ ] Rollback plan

---

**Versão:** 2.0  
**Data:** 2026-01-14  
**Metodologia:** DDD + SOLID + Clean Code + TDD
