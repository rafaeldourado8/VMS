# 🚀 Dual Pipeline & On-Demand - Documentação

## 📋 Arquitetura Implementada

### 1. Frontend (Lista/Mosaico)
- **Paginação:** 10 câmeras por página (hard-coded)
- **Lazy Loading:** Exibe apenas SNAPSHOT inicialmente
- **Player HLS:** Carrega apenas ao clicar na câmera
- **Mosaico:** Máximo 4 câmeras simultâneas
- **Protocolo:** HLS (Alta Qualidade, Estabilidade)

### 2. App Detecções (Visualização IA)
- **Protocolo:** WebRTC (Baixa Latência, Baixa Qualidade)
- **Stream:** `rtsp://mediamtx:8554/cam_X_ai`
- **Resolução:** 640x360 @ 15fps @ 500kbps
- **Features:** Bounding boxes + texto OCR desenhado

### 3. Backend Django

#### Model: `Deteccao`
```python
- placa: CharField(max_length=20, db_index=True)
- confianca: FloatField (0.0 a 1.0)
- snapshot_path: CharField (media/snapshots/YYYY/MM/DD/filename.jpg)
- camera: ForeignKey(Camera)
- vehicle_type: CharField (car, motorcycle, truck, bus, unknown)
- data_hora: DateTimeField (timestamp da detecção)
- created_at: DateTimeField (auto_now_add)
```

#### Endpoint de Ingestão
```
POST /api/deteccoes/ingest/
Headers:
  X-API-Key: {INGEST_API_KEY}
  Content-Type: application/json

Body:
{
  "camera_id": 1,
  "placa": "ABC1234",
  "confianca": 0.95,
  "snapshot_path": "snapshots/2025/01/15/cam1_ABC1234_143022.jpg",
  "vehicle_type": "car",
  "data_hora": "2025-01-15T14:30:22.123456"
}
```

### 4. Microsserviço IA (FastAPI)

#### Pipeline de Processamento
```
RTSP Input (On-Demand)
    ↓
YOLOv11 (mercosul_v1.pt)
    ↓
EasyOCR (pt)
    ↓
Desenha Bounding Boxes + Texto
    ↓
├─→ Salva Snapshot → POST Django
└─→ Redimensiona 640x360 → FFmpeg → RTSP MediaMTX
```

#### Configuração MediaMTX
```yaml
pathDefaults:
  sourceOnDemand: yes
  sourceOnDemandStartTimeout: 10s
  sourceOnDemandCloseAfter: 30s
  maxReaders: 12
```

## 🔧 Instalação e Configuração

### 1. Variáveis de Ambiente (.env)
```bash
# IA Service
YOLO_WEIGHTS=/app/models/mercosul_v1.pt
INGEST_API_KEY=your-secure-api-key-here

# Django
MEDIA_ROOT=/app/media
```

### 2. Dependências Python (IA Service)
```bash
pip install ultralytics easyocr opencv-python-headless requests
```

### 3. Migrations Django
```bash
cd backend
python manage.py makemigrations deteccoes
python manage.py migrate
```

### 4. Estrutura de Diretórios
```
vms system/
├── media/
│   └── snapshots/
│       └── 2025/
│           └── 01/
│               └── 15/
│                   └── cam1_ABC1234_143022.jpg
├── services/
│   └── ai_detection/
│       ├── detection_service.py
│       └── models/
│           └── mercosul_v1.pt
```

## 🚀 Como Usar

### Iniciar Detecção para uma Câmera
```python
from detection_service import AIDetectionService
import os

service = AIDetectionService(
    camera_id=1,
    rtsp_url="rtsp://admin:senha@192.168.1.100:554/stream",
    django_api_url="http://backend:8000/api/deteccoes/ingest/",
    api_key=os.getenv('INGEST_API_KEY')
)

thread = service.start()
```

### Visualizar Stream IA (Frontend)
```javascript
// WebRTC Player
const player = new RTCPeerConnection();
const streamUrl = `http://mediamtx:8889/cam_${cameraId}_ai/whep`;

// Conecta ao stream WebRTC
fetch(streamUrl, {
  method: 'POST',
  headers: { 'Content-Type': 'application/sdp' },
  body: await player.createOffer()
});
```

### Consultar Detecções (Django)
```python
# Últimas 10 detecções da câmera 1
deteccoes = Deteccao.objects.filter(camera_id=1)[:10]

for det in deteccoes:
    print(f"{det.placa} - {det.confianca:.2f} - {det.snapshot_url}")
```

## 📊 Performance

### Recursos por Câmera (IA Ativa)
- **CPU:** ~15-20% (1 core)
- **RAM:** ~500MB (modelos carregados)
- **Rede:** ~500kbps (saída WebRTC)
- **Disco:** ~50KB/detecção (snapshot)

### Limites Recomendados
- **Máximo 4 câmeras com IA simultânea** (mosaico)
- **Máximo 12 câmeras HLS simultâneas** (visualização comum)
- **On-Demand:** Stream fecha após 30s sem viewers

## 🔍 Troubleshooting

### Stream IA não aparece
```bash
# Verifica se o MediaMTX está recebendo
curl http://mediamtx:9997/v3/paths/list

# Verifica logs do FFmpeg
docker logs ai_detection_service
```

### Detecções não chegam no Django
```bash
# Testa endpoint manualmente
curl -X POST http://backend:8000/api/deteccoes/ingest/ \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"camera_id": 1, "placa": "TEST123", "confianca": 0.9, ...}'
```

### Snapshots não salvam
```bash
# Verifica permissões
docker exec backend ls -la /app/media/snapshots/

# Cria diretório manualmente
docker exec backend mkdir -p /app/media/snapshots/2025/01/15
```

## 📝 Próximos Passos

1. ✅ Implementar endpoint Django `/api/deteccoes/ingest/`
2. ✅ Criar view de listagem de detecções
3. ✅ Integrar frontend com WebRTC player
4. ⏳ Adicionar filtros por data/câmera/placa
5. ⏳ Implementar exportação de relatórios
6. ⏳ Dashboard de estatísticas em tempo real

## 🎯 Regras de Negócio Implementadas

- ✅ Paginação de 10 câmeras
- ✅ Lazy loading com snapshot
- ✅ Mosaico limitado a 4 câmeras
- ✅ HLS para visualização comum
- ✅ WebRTC para visualização IA
- ✅ OCR com persistência
- ✅ Snapshots organizados por data
- ✅ On-Demand streaming
- ✅ Dual pipeline (dados + vídeo)

---

**Versão:** 1.0.0  
**Data:** 2025-01-15  
**Autor:** Arquiteto de Software Sênior (VMS Especialista)
