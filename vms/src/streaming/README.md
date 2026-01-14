# 🎬 Módulo Streaming

## 📋 Responsabilidade

Gerenciar streaming HLS via MediaMTX e gravação cíclica 24/7 com notificações de expiração.

---

## 🏗️ Arquitetura

```
Câmera RTSP/RTMP → MediaMTX → ┬─ WebRTC (live, baixa latência)
                               ├─ HLS (gravação + fallback)
                               ├─ LL-HLS (thumbnail)
                               └─ FFmpeg → Snapshot (capa)
                                     ↓
                               Recording Service
                                     ↓
                               Storage Cíclico
                               (7/15/30 dias)
```

### Protocolos por Uso

| Protocolo | Uso | Latência | Qualidade |
|-----------|-----|----------|----------|
| **WebRTC** | Visualização ao vivo | < 500ms | **Excepcional (1080p 30fps)** |
| **HLS** | Gravação + Fallback | 2-6s | Alta (1080p 30fps) |
| **LL-HLS** | Thumbnail da câmera | 1-2s | Média (720p 15fps) |
| **Snapshot** | Capa da câmera (FFmpeg) | Instantâneo | Alta (1080p) |

---

## 📦 Estrutura

```
streaming/
├── domain/
│   ├── entities/
│   │   ├── stream.py              ✅ Stream HLS
│   │   └── recording.py           ✅ Gravação cíclica
│   ├── value_objects/
│   │   └── stream_status.py       ✅ Active/Stopped/Error
│   ├── repositories/
│   │   ├── stream_repository.py   ✅ Interface
│   │   ├── recording_repository.py ✅ Interface
│   │   └── streaming_provider.py  ✅ Interface MediaMTX
│   └── events/
│
├── application/
│   ├── use_cases/
│   │   ├── start_stream.py        ✅ Iniciar stream
│   │   └── stop_stream.py         ✅ Parar stream
│   └── services/
│       └── recording_cleanup.py   ✅ Limpeza de gravações
│
├── infrastructure/
│   ├── django/
│   │   ├── models.py              ✅ StreamModel
│   │   └── admin.py               ✅ Django Admin
│   └── mediamtx/
│       └── provider.py            ✅ MediaMTX adapter
│
└── tests/
    └── unit/
        ├── test_stream_entity.py      ✅ 3 tests
        └── test_recording_entity.py   ✅ 5 tests
```

---

## 🎯 Domain

### Stream Entity

```python
@dataclass
class Stream:
    id: str
    camera_id: str
    hls_url: str
    status: str = 'stopped'
    started_at: datetime | None = None
```

### Recording Entity

```python
@dataclass
class Recording:
    id: str
    camera_id: str
    file_path: str
    started_at: datetime
    is_permanent: bool = False
    
    def should_delete(self, retention_days: int) -> bool:
        if self.is_permanent:
            return False
        age = datetime.now() - self.started_at
        return age.days >= retention_days
```

---

## 🔄 Fluxo de Streaming

### 1. Iniciar Stream (Múltiplos Protocolos)

```python
use_case = StartStreamUseCase(stream_repo, mediamtx_provider)
result = use_case.execute(
    camera_id='cam-1',
    stream_url='rtsp://192.168.1.100/stream'
)
# Resultado:
# {
#     'webrtc_url': 'webrtc://mediamtx:8889/camera_cam-1',
#     'hls_url': 'http://mediamtx:8888/camera_cam-1/index.m3u8',
#     'll_hls_url': 'http://mediamtx:8888/camera_cam-1/ll.m3u8',
#     'snapshot_url': 'http://api:8000/cameras/cam-1/snapshot.jpg'
# }
```

### 2. MediaMTX Provider

```python
class MediaMTXProvider:
    def create_stream(self, camera_id: str, stream_url: str) -> dict:
        path = f"camera_{camera_id}"
        
        # Configura MediaMTX para receber RTSP/RTMP
        # MediaMTX automaticamente cria:
        # - WebRTC (porta 8889)
        # - HLS (porta 8888)
        # - LL-HLS (porta 8888)
        
        return {
            'webrtc_url': f"webrtc://{host}:8889/{path}",
            'hls_url': f"http://{host}:8888/{path}/index.m3u8",
            'll_hls_url': f"http://{host}:8888/{path}/ll.m3u8"
        }
```

### 3. Snapshot Service (FFmpeg)

```python
class SnapshotService:
    def capture_frame(self, camera_id: str) -> str:
        # Captura 1 frame do LL-HLS
        ll_hls_url = f"http://mediamtx:8888/camera_{camera_id}/ll.m3u8"
        
        # FFmpeg captura frame
        ffmpeg -i {ll_hls_url} \
               -vframes 1 \
               -q:v 2 \
               /snapshots/{camera_id}.jpg
        
        return f"/snapshots/{camera_id}.jpg"
```

### 4. Frontend - Uso dos Protocolos

```javascript
// 1. Capa da câmera (Snapshot)
<img src="/api/cameras/cam-1/snapshot.jpg" />

// 2. Visualização ao vivo (WebRTC - baixa latência)
<video id="live" autoplay />
const pc = new RTCPeerConnection();
pc.addTransceiver('video', {direction: 'recvonly'});
// Conecta ao webrtc://mediamtx:8889/camera_cam-1

// 3. Fallback (HLS - se WebRTC falhar)
if (!webrtcSupported) {
  const hls = new Hls();
  hls.loadSource('http://mediamtx:8888/camera_cam-1/index.m3u8');
  hls.attachMedia(video);
}

// 4. Thumbnail (LL-HLS - atualização rápida)
<img src="http://mediamtx:8888/camera_cam-1/ll.m3u8" />
```

---

## 💾 Gravação Cíclica

### Regras

| Plano | Retenção | Comportamento |
|-------|----------|---------------|
| Basic | 7 dias | Deleta após 7 dias |
| Pro | 15 dias | Deleta após 15 dias |
| Premium | 30 dias | Deleta após 30 dias |

### Clipes Permanentes
- Usuário marca gravação como permanente
- `is_permanent = True`
- **Nunca é deletada** no ciclo

### Notificações
- **1 dia antes** da exclusão
- Service: `RecordingCleanupService.get_expiring_soon()`

---

## 📊 Testes e Qualidade

### Testes Unitários
```
✅ 8 passed in 0.28s
✅ 99% de cobertura
```

### Complexidade Ciclomática
```
✅ Média: A (1.60)
✅ 48 blocos analisados
```

### Detalhamento

| Componente | Complexidade | Status |
|------------|--------------|--------|
| Stream entity | A (2) | ✅ |
| Recording entity | A (3) | ✅ |
| StartStreamUseCase | A (3) | ✅ |
| StopStreamUseCase | A (3) | ✅ |
| RecordingCleanupService | A (3) | ✅ |
| MediaMTXProvider | A (3) | ✅ |

---

## ✅ Implementado

### Domain
- [x] Stream entity
- [x] Recording entity (com lógica de expiração)
- [x] StreamStatus VO
- [x] IStreamRepository
- [x] IRecordingRepository
- [x] IStreamingProvider (MediaMTX)

### Application
- [x] StartStreamUseCase
- [x] StopStreamUseCase
- [x] RecordingCleanupService

### Infrastructure
- [x] MediaMTXProvider (adapter)
- [x] StreamModel (Django)
- [x] StreamAdmin

### Tests
- [x] 8 testes unitários
- [x] 99% cobertura
- [x] Teste de expiração
- [x] Teste de clipes permanentes

---

## 🎨 Django Admin

### Visualização
- Camera ID
- Status (Active/Stopped/Error)
- HLS URL
- Data de início
- Datas de criação/atualização

### Ações
- Parar streams selecionados

---

## 🚀 Próximo

- [ ] Migrations
- [ ] Recording Service (FFmpeg)
- [ ] Celery task para cleanup
- [ ] Notificações de expiração
- [ ] Integração com módulo Cameras
