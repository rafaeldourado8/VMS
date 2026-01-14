# 🏗️ Arquitetura VMS - Bounded Contexts

## 📋 Estrutura Modular

Cada módulo segue **Clean Architecture** com 4 camadas:

```
src/
├── admin/           # Gestão de usuários e autenticação
├── cidades/         # Multi-tenant (1 DB por cidade)
├── cameras/         # CRUD de câmeras (RTSP/RTMP)
├── streaming/       # MediaMTX + HLS
├── lpr/             # Detecção de placas (YOLO + OCR)
└── sentinela/       # Busca retroativa (Rekognition)
```

---

## 🎯 Bounded Contexts

### 1. Admin (Usuários + Auth)
**Responsabilidade:** Autenticação, autorização, gestão de usuários

**Domain:**
- User entity
- Role, Permission VOs
- IUserRepository

**Infrastructure:**
- Django User Model (adapter)
- JWT/Session auth
- DB: `default`

---

### 2. Cidades (Multi-tenant)
**Responsabilidade:** Gestão de cidades (tenants) e planos

**Domain:**
- City entity
- PlanType VO (Basic/Pro/Premium)
- ICityRepository

**Infrastructure:**
- CityModel (Django)
- Multi-tenant Router
- DB: `default` (metadados)

**Regras:**
- 1 DB por cidade
- Max 1000 câmeras
- Max 20 LPR
- Retenção: 7/15/30 dias

---

### 3. Cameras (CRUD)
**Responsabilidade:** Gerenciar câmeras (RTSP/RTMP)

**Domain:**
- Camera entity
- CameraType VO (RTSP/RTMP)
- CameraStatus VO
- ICameraRepository

**Infrastructure:**
- CameraModel (Django)
- DB: `cidade_{slug}` (tenant)

**Regras:**
- RTSP: LPR ativo (max 20)
- RTMP: Só gravação (max 1000)

---

### 4. Streaming (MediaMTX)
**Responsabilidade:** Streaming HLS + Gravação 24/7

**Domain:**
- Stream entity
- Recording entity
- IStreamingProvider
- IRecordingService

**Infrastructure:**
- MediaMTX adapter
- FFmpeg recorder
- Storage (S3/local)
- DB: `cidade_{slug}`

**Regras:**
- Gravação cíclica (7/15/30 dias)
- Notificação 1 dia antes
- Clipes permanentes

---

### 5. LPR (Detecção)
**Responsabilidade:** Detecção de placas em tempo real

**Domain:**
- Detection entity
- Plate VO
- Confidence VO
- IDetectionProvider

**Infrastructure:**
- YOLO adapter
- OCR adapter
- Celery tasks
- WebSocket
- DB: `cidade_{slug}`

**Regras:**
- Apenas câmeras RTSP
- Max 20 por cidade
- Confidence > 0.75

---

### 6. Sentinela (Busca)
**Responsabilidade:** Busca retroativa em gravações

**Domain:**
- VehicleSearch entity
- Trajectory entity
- IRekognitionProvider

**Infrastructure:**
- Rekognition adapter
- Celery tasks (async)
- DB: `cidade_{slug}`

**Regras:**
- Busca em todas as 1000 câmeras
- Processa gravações históricas
- Timeline ordenada

---

## 🔄 Comunicação entre Contextos

### Eventos de Domínio

```python
# cidades/domain/events.py
@dataclass
class CityCreatedEvent:
    city_id: str
    slug: str
    plan: str

# cameras/application/handlers.py
class CityCreatedHandler:
    def handle(self, event: CityCreatedEvent):
        # Cria tabelas no novo DB
        self._create_tenant_database(event.slug)
```

### Shared Kernel (Mínimo)

```
src/
└── shared/
    ├── domain/
    │   └── value_objects/
    │       ├── entity_id.py
    │       └── timestamp.py
    └── infrastructure/
        └── event_bus.py
```

---

## 📦 Estrutura de Cada Módulo

```
cameras/
├── domain/
│   ├── entities/
│   │   └── camera.py          # Python puro
│   ├── value_objects/
│   │   ├── camera_type.py
│   │   └── camera_status.py
│   ├── repositories/
│   │   └── camera_repository.py  # Interface
│   └── events/
│       └── camera_events.py
│
├── application/
│   ├── use_cases/
│   │   ├── create_camera.py
│   │   ├── activate_camera.py
│   │   └── list_cameras.py
│   ├── dtos/
│   │   └── camera_dto.py
│   └── handlers/
│       └── event_handlers.py
│
├── infrastructure/
│   ├── django/
│   │   ├── models.py          # CameraModel (adapter)
│   │   ├── admin.py           # Django Admin
│   │   ├── migrations/
│   │   └── repositories.py    # DjangoCameraRepository
│   ├── cache/
│   │   └── redis_cache.py
│   └── messaging/
│       └── rabbitmq.py
│
└── presentation/
    └── api/
        ├── views.py           # REST endpoints
        ├── serializers.py
        └── urls.py
```

---

## 🎯 Dependências entre Camadas

```
Presentation → Application → Domain ← Infrastructure
                                ↑
                          (implementa)
```

### Regras:
1. **Domain** não depende de nada (Python puro)
2. **Application** depende só de Domain
3. **Infrastructure** implementa interfaces do Domain
4. **Presentation** usa Application (Use Cases)
5. **Django** só em Infrastructure e Presentation

---

## 🚀 Sprint 1: Implementação

### Ordem de Desenvolvimento

1. **Cidades** (base multi-tenant)
   - Domain: City entity
   - Infrastructure: CityModel + Router
   - Admin: CityAdmin

2. **Admin** (autenticação)
   - Domain: User entity
   - Infrastructure: Django User
   - Admin: UserAdmin

3. **Cameras** (CRUD)
   - Domain: Camera entity
   - Infrastructure: CameraModel
   - Admin: CameraAdmin

---

## 📝 Exemplo Completo: Cameras

### Domain (Python Puro)

```python
# cameras/domain/entities/camera.py
from dataclasses import dataclass

@dataclass
class Camera:
    id: str
    name: str
    type: str  # 'rtsp' ou 'rtmp'
    rtsp_url: str
    city_id: str
    status: str = 'inactive'
    
    def activate(self):
        self.status = 'active'
    
    def is_lpr_enabled(self) -> bool:
        return self.type == 'rtsp'
```

### Application (Use Case)

```python
# cameras/application/use_cases/create_camera.py
from dataclasses import dataclass

@dataclass
class CreateCameraRequest:
    name: str
    type: str
    rtsp_url: str
    city_id: str

class CreateCameraUseCase:
    def __init__(self, repo):
        self._repo = repo
    
    def execute(self, req: CreateCameraRequest) -> str:
        camera = Camera(
            id=str(uuid4()),
            name=req.name,
            type=req.type,
            rtsp_url=req.rtsp_url,
            city_id=req.city_id
        )
        self._repo.save(camera)
        return camera.id
```

### Infrastructure (Django)

```python
# cameras/infrastructure/django/models.py
from django.db import models

class CameraModel(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10)
    rtsp_url = models.URLField()
    city_id = models.UUIDField()
    status = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'cameras'
    
    def to_entity(self):
        from cameras.domain.entities import Camera
        return Camera(
            id=str(self.id),
            name=self.name,
            type=self.type,
            rtsp_url=self.rtsp_url,
            city_id=str(self.city_id),
            status=self.status
        )
```

```python
# cameras/infrastructure/django/admin.py
from django.contrib import admin

@admin.register(CameraModel)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'status', 'city_id']
    list_filter = ['type', 'status']
    actions = ['activate_cameras']
    
    def activate_cameras(self, request, queryset):
        use_case = ActivateCameraUseCase(repo)
        for cam in queryset:
            use_case.execute(str(cam.id))
```

### Presentation (API)

```python
# cameras/presentation/api/views.py
from rest_framework.views import APIView

class CreateCameraView(APIView):
    def post(self, request):
        use_case = CreateCameraUseCase(repo)
        req = CreateCameraRequest(**request.data)
        camera_id = use_case.execute(req)
        return Response({'id': camera_id}, status=201)
```

---

## ✅ Checklist Sprint 1

### Cidades
- [ ] City entity
- [ ] CityModel
- [ ] Multi-tenant Router
- [ ] CityAdmin

### Admin
- [ ] User entity
- [ ] Django User integration
- [ ] UserAdmin

### Cameras
- [ ] Camera entity
- [ ] CameraModel
- [ ] CameraRepository
- [ ] CreateCameraUseCase
- [ ] CameraAdmin

---

**Pronto para começar a implementação?** 🚀
