# 🚀 Sprints VMS - Clean Architecture + DDD

## 📋 Visão Geral

Desenvolvimento do VMS em **7 sprints** de 1 semana cada, seguindo **Clean Architecture** e **Domain-Driven Design**.

### ⚠️ Princípio Fundamental: Django como Ferramenta

```
❌ ERRADO: Domain depende de Django
✅ CORRETO: Django depende do Domain

Domain (puro Python) → Application → Infrastructure (Django/FastAPI)
```

**Django Admin** é usado como **ferramenta de administração**, mas:
- Domain não conhece Django
- Entities são Python puro
- Django Models são apenas adapters (Infrastructure)

**FastAPI** é usado para **APIs assíncronas** (streaming, LPR)

---

## 📅 Cronograma

| Sprint | Duração | Foco | Entregável |
|--------|---------|------|------------|
| **Sprint 1** | 7 dias | Core + Multi-tenant | ✅ Domain + DB por cidade |
| **Sprint 2** | 7 dias | Streaming + Gravação | ✅ MediaMTX + Recording 24/7 |
| **Sprint 3** | 7 dias | LPR Detection | ✅ YOLO + OCR em 20 câmeras |
| **Sprint 4** | 7 dias | Admin + Auth | ⏳ Django Admin + JWT |
| **Sprint 5** | 7 dias | Integração + FastAPI | ⏳ Módulos integrados + Async |
| **Sprint 6** | 7 dias | YOLO Real + Recording | ⏳ Modelo treinado + FFmpeg |
| **Sprint 7** | 7 dias | Deploy + Monitoring | ⏳ Docker + Prometheus |

---

## ⚠️ Sentinela - Pós-MVP

**Sentinela (busca retroativa) não faz parte do MVP:**
- Requer modelo YOLO treinado específico para busca
- Requer integração com AWS Rekognition (custos)
- Requer processamento pesado de vídeos
- Será desenvolvido após MVP validado

**MVP inclui (Sprints 1-7):**
- ✅ Cidades (multi-tenant)
- ✅ Cameras (auto-detecção RTSP/RTMP)
- ✅ Streaming (MediaMTX + HLS)
- ✅ LPR (detecção em tempo real)
- ⏳ Admin + Auth (JWT)
- ⏳ Integração + FastAPI
- ⏳ Deploy + Monitoring

---

## 🏗️ Arquitetura DDD

### Camadas

```
┌─────────────────────────────────────────┐
│  Presentation (Django Admin, API REST)  │  ← Django aqui
├─────────────────────────────────────────┤
│  Application (Use Cases, DTOs)          │  ← Orquestração
├─────────────────────────────────────────┤
│  Domain (Entities, VOs, Interfaces)     │  ← Python puro
├─────────────────────────────────────────┤
│  Infrastructure (Django ORM, Redis...)  │  ← Implementações
└─────────────────────────────────────────┘
```

### Estrutura de Pastas

```
vms/
├── sprints/              # Documentação dos sprints
│   ├── sprint-1/
│   ├── sprint-2/
│   ├── sprint-3/
│   └── sprint-4/
└── src/
    ├── domain/           # Python puro (sem Django)
    │   ├── entities/
    │   ├── value_objects/
    │   ├── repositories/  # Interfaces
    │   └── services/
    ├── application/      # Use Cases
    │   ├── use_cases/
    │   └── dtos/
    ├── infrastructure/   # Django aqui
    │   ├── django/       # Models, Admin, Migrations
    │   ├── cache/        # Redis
    │   └── messaging/    # RabbitMQ
    └── presentation/     # API REST
        └── api/
```

---

## 🎯 Sprint 1: Core + Multi-tenant (7 dias)

### Objetivo
Base do sistema com multi-tenant (1 DB por cidade) e planos de armazenamento.

### Entregáveis
- [x] Domain: Entities (Camera, City, Plan, User)
- [x] Domain: Value Objects (CameraType, PlanType, RetentionDays)
- [x] Domain: Repository Interfaces
- [x] Infrastructure: Django Models (adapters)
- [x] Infrastructure: Multi-tenant Router
- [x] Application: Use Cases (CreateCity, AddCamera)
- [x] Presentation: Django Admin (observabilidade total)
- [x] Migrations + Seeds

### Django Admin
- CRUD completo de cidades
- CRUD completo de câmeras
- Visualização de planos
- Métricas por cidade

---

## 🎯 Sprint 2: Streaming + Gravação (7 dias)

### Objetivo
Streaming HLS + Gravação cíclica 24/7 (7/15/30 dias).

### Entregáveis
- [x] Domain: Stream, Recording entities
- [x] Infrastructure: MediaMTX adapter
- [x] Infrastructure: Recording Service (FFmpeg)
- [x] Application: StartStream, StopStream Use Cases
- [x] Application: Recording Pipeline (Celery)
- [x] Presentation: Django Admin (controle de streams)
- [x] Notificações (1 dia antes da exclusão)

### Django Admin
- Status de streams por câmera
- Controle manual de gravação
- Visualização de espaço usado
- Alertas de expiração

---

## 🎯 Sprint 3: LPR Detection (7 dias)

### Objetivo
Detecção de placas em tempo real (até 20 câmeras RTSP).

### Entregáveis
- [x] Domain: Detection, Plate entities
- [x] Infrastructure: YOLO + OCR adapter
- [x] Application: ProcessFrame Use Case
- [x] Application: Detection Pipeline (Celery)
- [x] Presentation: Django Admin (detecções)
- [x] WebSocket (notificações real-time)

### Django Admin
- Lista de detecções por câmera
- Filtros (placa, data, confiança)
- Estatísticas de detecção
- Blacklist management

---

## 🎯 Sprint 4: Sentinela + Deploy (7 dias)

### Objetivo
Busca retroativa em gravações + Deploy produção.

### Entregáveis
- [x] Domain: Search, Trajectory entities
- [x] Infrastructure: Rekognition adapter
- [x] Application: SearchVehicle Use Case
- [x] Application: Sentinela Pipeline (async)
- [x] Presentation: Django Admin (buscas)
- [x] Docker Compose produção
- [x] Monitoring (Prometheus + Grafana)

### Django Admin
- Interface de busca
- Histórico de buscas
- Resultados com timeline
- Exportação de evidências

---

## 🔧 Django Admin: Observabilidade Total

### Princípios
1. **Admin não é Domain** - Admin usa Use Cases
2. **Observabilidade** - Tudo visível no admin
3. **Controle** - Ações manuais quando necessário
4. **Métricas** - Dashboards integrados

### Exemplo de Integração

```python
# domain/entities/camera.py (Python puro)
class Camera:
    def __init__(self, id: str, name: str, type: CameraType):
        self.id = id
        self.name = name
        self.type = type
    
    def activate(self):
        self.status = CameraStatus.ACTIVE

# infrastructure/django/models.py (Adapter)
class CameraModel(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10)
    
    def to_entity(self) -> Camera:
        return Camera(str(self.id), self.name, CameraType(self.type))

# infrastructure/django/admin.py (Ferramenta)
@admin.register(CameraModel)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'status', 'city']
    actions = ['activate_cameras']
    
    def activate_cameras(self, request, queryset):
        # Usa Use Case, não manipula diretamente
        use_case = ActivateCameraUseCase(repo)
        for camera in queryset:
            use_case.execute(camera.id)
```

---

## 📊 Métricas de Sucesso

### Sprint 1
- ✅ 3+ cidades cadastradas
- ✅ 50+ câmeras distribuídas
- ✅ Multi-tenant funcionando

### Sprint 2
- ✅ 1000 câmeras streamando
- ✅ Gravação 24/7 ativa
- ✅ Notificações funcionando

### Sprint 3
- ✅ 20 câmeras com LPR
- ✅ 100+ detecções/hora
- ✅ WebSocket real-time

### Sprint 4
- ✅ Sentinela operacional
- ✅ Deploy em produção
- ✅ Monitoring ativo

---

## 🚀 Próximo Passo

Começar **Sprint 1** com:
1. Domain entities (Python puro)
2. Repository interfaces
3. Django Models (adapters)
4. Multi-tenant router
5. Django Admin básico

**Vamos começar?** 🎯
