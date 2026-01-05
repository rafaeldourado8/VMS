# 🔄 Plano de Migração - Remoção de Código Legado

## 📋 Objetivo

Remover código antigo e migrar completamente para arquitetura DDD.

---

## 🗑️ Módulos a Remover

### Backend Django

#### Apps Legados (mover para `_legacy/` antes de remover)
```
backend/apps/
├── cameras/          # ❌ Substituído por domain/monitoring + infrastructure
│   ├── models.py     # → infrastructure/persistence/django/models/camera_model.py
│   ├── services.py   # → application/monitoring/handlers/
│   ├── views.py      # → Refatorar para usar handlers
│   └── serializers.py
│
├── deteccoes/        # ❌ Substituído por domain/detection + infrastructure
│   ├── models.py     # → infrastructure/persistence/django/models/detection_model.py
│   ├── services.py   # → application/detection/handlers/
│   ├── views.py      # → Refatorar para usar handlers
│   └── serializers.py
│
├── analytics/        # ⚠️ Avaliar necessidade
├── clips/            # ⚠️ Avaliar necessidade
├── configuracoes/    # ⚠️ Avaliar necessidade
├── dashboard/        # ⚠️ Avaliar necessidade
├── suporte/          # ⚠️ Avaliar necessidade
├── thumbnails/       # ⚠️ Avaliar necessidade
└── usuarios/         # ⚠️ Manter (autenticação)
```

### Streaming Service

```
services/streaming/
├── main.py           # ❌ Substituído por api/main_ddd.py
├── drift_monitor.py  # ⚠️ Avaliar se integrar
└── test_*.py         # ❌ Substituído por tests/
```

### AI Detection Service

```
services/ai_detection/
├── main.py           # ❌ Substituído por api/main.py (DDD)
├── camera_manager.py # ❌ Substituído por infrastructure/repositories/
├── detection_service.py # ❌ Substituído por domain/detection/services/
└── ffmpeg_worker.py  # ⚠️ Avaliar se integrar
```

### Frontend

```
frontend/src/
├── services/api.ts   # ❌ Substituído por infrastructure/api/ApiClient.ts
├── store/            # ⚠️ Avaliar se manter (Zustand)
└── utils/            # ⚠️ Avaliar necessidade
```

---

## 📝 Etapas de Migração

### Fase 1: Backup e Preparação (1 dia)

1. **Criar branch de backup**
```bash
git checkout -b backup-before-cleanup
git push origin backup-before-cleanup
```

2. **Criar pasta `_legacy/`**
```bash
mkdir backend/_legacy
mkdir services/streaming/_legacy
mkdir services/ai_detection/_legacy
mkdir frontend/src/_legacy
```

3. **Documentar dependências**
- Listar todas as importações dos módulos antigos
- Identificar código ainda em uso

### Fase 2: Backend Django (2-3 dias)

#### 2.1 Migrar Views para Handlers

**Cameras:**
```python
# Antes (apps/cameras/views.py)
class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer

# Depois (interfaces/api/v1/cameras/views.py)
@api_view(['POST'])
def create_camera(request):
    command = CreateCameraCommand(**request.data)
    camera = create_camera_handler.handle(command)
    return Response(CameraSerializer(camera).data)
```

**Detections:**
```python
# Antes (apps/deteccoes/views.py)
class DeteccaoViewSet(viewsets.ModelViewSet):
    queryset = Deteccao.objects.all()

# Depois (interfaces/api/v1/detections/views.py)
@api_view(['POST'])
def create_detection(request):
    command = ProcessDetectionCommand(**request.data)
    detection = process_detection_handler.handle(command)
    return Response(DetectionSerializer(detection).data)
```

#### 2.2 Atualizar URLs

```python
# config/urls.py
urlpatterns = [
    # Novo (DDD)
    path('api/v1/cameras/', include('interfaces.api.v1.cameras.urls')),
    path('api/v1/detections/', include('interfaces.api.v1.detections.urls')),
    
    # Antigo (deprecar)
    # path('api/cameras/', include('apps.cameras.urls')),  # DEPRECATED
    # path('api/deteccoes/', include('apps.deteccoes.urls')),  # DEPRECATED
]
```

#### 2.3 Mover para `_legacy/`

```bash
mv backend/apps/cameras backend/_legacy/
mv backend/apps/deteccoes backend/_legacy/
```

### Fase 3: Streaming Service (1 dia)

#### 3.1 Substituir main.py

```bash
# Renomear antigo
mv services/streaming/main.py services/streaming/_legacy/main_old.py

# Usar novo
mv services/streaming/api/main_ddd.py services/streaming/main.py
```

#### 3.2 Atualizar docker-compose.yml

```yaml
# Antes
streaming:
  command: uvicorn main:app --host 0.0.0.0 --port 8001

# Depois (já está correto)
streaming:
  command: uvicorn main:app --host 0.0.0.0 --port 8001
```

### Fase 4: AI Detection Service (1 dia)

#### 4.1 Substituir main.py

```bash
# Renomear antigo
mv services/ai_detection/main.py services/ai_detection/_legacy/main_old.py

# Usar novo
mv services/ai_detection/api/main.py services/ai_detection/main.py
```

#### 4.2 Integrar FFmpeg Worker

```python
# Criar adapter em infrastructure/
# infrastructure/ffmpeg/ffmpeg_adapter.py
class FFmpegAdapter:
    def extract_frame(self, rtsp_url: str) -> bytes:
        # Usar código do ffmpeg_worker.py antigo
        pass
```

### Fase 5: Frontend (1 dia)

#### 5.1 Atualizar Imports

```typescript
// Antes
import { api } from '../services/api';

// Depois
import { apiClient } from '../infrastructure/api/ApiClient';
```

#### 5.2 Refatorar Componentes

```typescript
// Antes (CamerasPage.tsx)
const { data } = useQuery('cameras', () => api.get('/cameras'));

// Depois
const { cameras } = useCameras();
```

#### 5.3 Mover para `_legacy/`

```bash
mv frontend/src/services frontend/src/_legacy/
```

### Fase 6: Testes e Validação (2 dias)

#### 6.1 Executar Testes

```bash
# Backend
cd backend
python -m pytest tests/ -v

# Streaming
cd services/streaming
python -m pytest tests/ -v

# AI Detection
cd services/ai_detection
python -m pytest tests/ -v
```

#### 6.2 Testes E2E

- Criar câmera via API
- Provisionar stream
- Ativar IA
- Desenhar ROI
- Verificar detecções

#### 6.3 Validar Performance

- Latência de streaming < 2s
- CPU AI < 1% por câmera
- Memória estável

### Fase 7: Remoção Final (1 dia)

#### 7.1 Remover `_legacy/`

```bash
# Após validação completa
rm -rf backend/_legacy
rm -rf services/streaming/_legacy
rm -rf services/ai_detection/_legacy
rm -rf frontend/src/_legacy
```

#### 7.2 Limpar Imports

```bash
# Buscar imports antigos
grep -r "from apps.cameras" backend/
grep -r "from apps.deteccoes" backend/

# Remover se encontrar
```

#### 7.3 Atualizar Documentação

- README.md
- CONTEXT.md
- API docs

---

## ✅ Checklist de Validação

### Backend
- [ ] Todas as views migradas para handlers
- [ ] URLs atualizadas
- [ ] Testes passando
- [ ] Imports limpos
- [ ] `apps/` removido

### Streaming
- [ ] main.py usando DDD
- [ ] Endpoints funcionando
- [ ] Testes passando
- [ ] Performance mantida

### AI Detection
- [ ] main.py usando DDD
- [ ] Toggle IA funcionando
- [ ] ROI funcionando
- [ ] Detecções funcionando

### Frontend
- [ ] Imports atualizados
- [ ] Componentes usando hooks
- [ ] API client funcionando
- [ ] ROI drawer funcionando

---

## 🚨 Riscos e Mitigações

### Risco 1: Quebra de API
**Mitigação:** Manter endpoints antigos com `@deprecated` por 1 sprint

### Risco 2: Perda de funcionalidade
**Mitigação:** Backup em branch separada

### Risco 3: Performance degradada
**Mitigação:** Testes de carga antes de remover

---

## 📊 Tempo Estimado

| Fase | Tempo | Status |
|------|-------|--------|
| 1. Backup | 1 dia | ⏳ |
| 2. Backend | 2-3 dias | ⏳ |
| 3. Streaming | 1 dia | ⏳ |
| 4. AI Detection | 1 dia | ⏳ |
| 5. Frontend | 1 dia | ⏳ |
| 6. Testes | 2 dias | ⏳ |
| 7. Remoção | 1 dia | ⏳ |
| **TOTAL** | **9-10 dias** | ⏳ |

---

## 🎯 Resultado Esperado

Após a migração:
- ✅ 100% código DDD
- ✅ 0% código legado
- ✅ Arquitetura limpa
- ✅ Manutenibilidade máxima
- ✅ Performance mantida/melhorada

---

**Status:** Aguardando aprovação para iniciar Fase 1
