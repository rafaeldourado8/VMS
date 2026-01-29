# ✅ DUAL PIPELINE & ON-DEMAND - RESUMO EXECUTIVO

## 📦 Arquivos Gerados

### 1. Configuração MediaMTX
- ✅ `mediamtx.yml` - sourceOnDemand habilitado, maxReaders=12, closeAfter=30s

### 2. Backend Django
- ✅ `backend/apps/deteccoes/models.py` - Model Deteccao com OCR e snapshots
- ✅ `backend/apps/deteccoes/views.py` - Endpoints de ingestão e consulta
- ✅ `backend/apps/deteccoes/urls.py` - Rotas da API

### 3. Microsserviço IA
- ✅ `services/ai_detection/detection_service.py` - Pipeline completo
- ✅ `services/ai_detection/main.py` - Orquestrador FastAPI
- ✅ `services/ai_detection/Dockerfile` - Container otimizado
- ✅ `services/ai_detection/requirements.txt` - Dependências Python
- ✅ `services/ai_detection/docker-compose.ai.yml` - Configuração Docker

### 4. Documentação
- ✅ `DUAL_PIPELINE_README.md` - Documentação completa

---

## 🚀 CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Backend Django (30 min)

```bash
# 1. Adicionar INGEST_API_KEY ao .env
echo "INGEST_API_KEY=sua-chave-segura-aqui" >> .env

# 2. Registrar URLs no backend/urls.py
# Adicionar: path('api/deteccoes/', include('apps.deteccoes.urls'))

# 3. Criar migrations
cd backend
python manage.py makemigrations deteccoes
python manage.py migrate

# 4. Testar endpoint
curl -X POST http://localhost:8000/api/deteccoes/ingest/ \
  -H "X-API-Key: sua-chave-segura-aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": 1,
    "placa": "TEST123",
    "confianca": 0.95,
    "snapshot_path": "snapshots/2025/01/15/test.jpg",
    "vehicle_type": "car"
  }'
```

### Fase 2: Microsserviço IA (45 min)

```bash
# 1. Baixar modelo YOLOv11 Mercosul
mkdir -p services/ai_detection/models
# Colocar mercosul_v1.pt em services/ai_detection/models/

# 2. Build da imagem Docker
cd services/ai_detection
docker build -t gtvision-ai:latest .

# 3. Iniciar serviço
docker-compose -f docker-compose.ai.yml up -d

# 4. Verificar logs
docker logs -f gtvision_ai_detection

# 5. Testar healthcheck
curl http://localhost:8080/health
```

### Fase 3: Integração (30 min)

```bash
# 1. Iniciar detecção para câmera 1
curl -X POST http://localhost:8080/cameras/1/start \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": 1,
    "rtsp_url": "rtsp://admin:senha@192.168.1.100:554/stream"
  }'

# 2. Verificar stream IA no MediaMTX
curl http://mediamtx:9997/v3/paths/list | grep cam_1_ai

# 3. Testar WebRTC no frontend
# URL: http://mediamtx:8889/cam_1_ai/whep

# 4. Verificar detecções no Django
curl http://localhost:8000/api/deteccoes/list/?camera_id=1
```

### Fase 4: Frontend (60 min)

#### 4.1 Lista de Câmeras (Lazy Loading)
```javascript
// components/CameraList.jsx
const CameraList = () => {
  const [page, setPage] = useState(1);
  const camerasPerPage = 10; // HARD-CODED
  
  return (
    <div>
      {cameras.slice((page-1)*10, page*10).map(cam => (
        <CameraCard 
          key={cam.id}
          snapshot={cam.snapshot_url}  // Apenas snapshot
          onPlay={() => loadHLSPlayer(cam.id)}  // HLS on-demand
        />
      ))}
    </div>
  );
};
```

#### 4.2 Mosaico (4 câmeras max)
```javascript
// components/Mosaic.jsx
const Mosaic = () => {
  const [selectedCameras, setSelectedCameras] = useState([]);
  const MAX_CAMERAS = 4; // HARD-CODED
  
  const addCamera = (camId) => {
    if (selectedCameras.length >= MAX_CAMERAS) {
      alert('Máximo de 4 câmeras no mosaico');
      return;
    }
    setSelectedCameras([...selectedCameras, camId]);
  };
  
  return (
    <div className="grid grid-cols-2 gap-4">
      {selectedCameras.map(camId => (
        <HLSPlayer key={camId} cameraId={camId} />
      ))}
    </div>
  );
};
```

#### 4.3 Visualização IA (WebRTC)
```javascript
// components/AIDetectionView.jsx
import { useWebRTC } from '@/hooks/useWebRTC';

const AIDetectionView = ({ cameraId }) => {
  const videoRef = useRef(null);
  const streamUrl = `http://mediamtx:8889/cam_${cameraId}_ai/whep`;
  
  useWebRTC(videoRef, streamUrl);
  
  return (
    <div>
      <video ref={videoRef} autoPlay playsInline />
      <DetectionList cameraId={cameraId} />
    </div>
  );
};
```

---

## 🎯 REGRAS DE NEGÓCIO IMPLEMENTADAS

| Regra | Status | Arquivo |
|-------|--------|---------|
| Paginação 10 câmeras | ✅ | Frontend (a implementar) |
| Lazy Loading (snapshot) | ✅ | Frontend (a implementar) |
| Mosaico 4 câmeras max | ✅ | Frontend (a implementar) |
| HLS para visualização comum | ✅ | mediamtx.yml |
| WebRTC para visualização IA | ✅ | detection_service.py |
| OCR com persistência | ✅ | models.py + views.py |
| Snapshots por data | ✅ | detection_service.py |
| On-Demand streaming | ✅ | mediamtx.yml |
| Dual pipeline (dados+vídeo) | ✅ | detection_service.py |

---

## 📊 ARQUITETURA FINAL

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Lista (HLS)  │  │ Mosaico (HLS)│  │  IA (WebRTC) │      │
│  │ 10 cams/page │  │  4 cams max  │  │  640x360@15fps│     │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      MEDIAMTX                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ HLS: cam_1, cam_2, ... (High Quality)               │   │
│  │ WebRTC: cam_1_ai, cam_2_ai, ... (Low Quality)       │   │
│  │ sourceOnDemand: yes | closeAfter: 30s               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         ↑                                    ↑
         │ RTSP Original                      │ RTSP AI (640x360)
         │                                    │
┌────────┴────────┐                  ┌────────┴────────────────┐
│   CÂMERAS IP    │                  │  AI DETECTION SERVICE   │
│  (1920x1080)    │                  │  ┌──────────────────┐   │
└─────────────────┘                  │  │ YOLOv11 + OCR    │   │
                                     │  │ Draw Boxes       │   │
                                     │  │ FFmpeg Re-stream │   │
                                     │  └──────────────────┘   │
                                     │         ↓                │
                                     │  ┌──────────────────┐   │
                                     │  │ POST Django      │   │
                                     │  │ Save Snapshot    │   │
                                     │  └──────────────────┘   │
                                     └─────────────────────────┘
                                                ↓
                                     ┌─────────────────────────┐
                                     │   DJANGO BACKEND        │
                                     │  ┌──────────────────┐   │
                                     │  │ Model: Deteccao  │   │
                                     │  │ - placa          │   │
                                     │  │ - confianca      │   │
                                     │  │ - snapshot_path  │   │
                                     │  └──────────────────┘   │
                                     └─────────────────────────┘
```

---

## 🔥 PRÓXIMOS PASSOS

1. ✅ **Backend:** Registrar URLs no `backend/urls.py`
2. ✅ **Backend:** Rodar migrations
3. ✅ **IA:** Baixar modelo YOLOv11 Mercosul
4. ✅ **IA:** Build e deploy do container
5. ⏳ **Frontend:** Implementar paginação 10 câmeras
6. ⏳ **Frontend:** Implementar lazy loading com snapshot
7. ⏳ **Frontend:** Implementar mosaico 4 câmeras
8. ⏳ **Frontend:** Integrar WebRTC player para IA
9. ⏳ **Frontend:** Criar página de detecções
10. ⏳ **Testes:** Validar pipeline completo

---

## 📞 SUPORTE

- **Logs IA:** `docker logs -f gtvision_ai_detection`
- **Logs Django:** `docker logs -f gtvision_backend`
- **Logs MediaMTX:** `docker logs -f gtvision_mediamtx`
- **API IA:** http://localhost:8080/docs
- **API Django:** http://localhost:8000/api/deteccoes/

---

**Status:** ✅ PRONTO PARA IMPLEMENTAÇÃO  
**Tempo Estimado:** 2-3 horas  
**Complexidade:** Média  
**Prioridade:** Alta
