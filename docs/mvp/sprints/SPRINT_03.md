# 🎯 SPRINT 3: SERVIÇO DE PLAYBACK

**Duração**: 1 semana  
**Objetivo**: Implementar API de playback que reutiliza MediaMTX

---

## TAREFAS

### 3.1 Criar Serviço de Playback (FastAPI)

**Arquivo**: `services/playback/main.py`

```python
import os
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="GTVision Playback Service")

RECORDINGS_PATH = "/recordings"
MEDIAMTX_API = "http://mediamtx:9997"
MEDIAMTX_AUTH = ("mediamtx_api_user", "GtV!sionMed1aMTX$2025")

class TimelineSegment(BaseModel):
    start: str
    end: str
    file_path: str
    size_bytes: int
    duration_seconds: int

@app.get("/cameras/{camera_id}/timeline")
def get_timeline(camera_id: int, date: str):
    """Retorna segmentos disponíveis para uma data."""
    cam_path = f"{RECORDINGS_PATH}/cam_{camera_id}"
    date_path = os.path.join(cam_path, date)
    
    if not os.path.exists(date_path):
        return {"segments": []}
    
    segments = []
    for file in sorted(os.listdir(date_path)):
        if file.endswith(".mp4"):
            hour = int(file.replace(".mp4", ""))
            file_path = os.path.join(date_path, file)
            
            start = datetime.strptime(f"{date} {hour:02d}:00:00", "%Y-%m-%d %H:%M:%S")
            end = start + timedelta(hours=1)
            
            segments.append({
                "start": start.isoformat(),
                "end": end.isoformat(),
                "file_path": file_path,
                "size_bytes": os.path.getsize(file_path),
                "duration_seconds": 3600
            })
    
    return {"segments": segments}

@app.post("/playback/start")
async def start_playback(camera_id: int, start_time: str):
    """Inicia playback via MediaMTX."""
    dt = datetime.fromisoformat(start_time)
    date_str = dt.strftime("%Y-%m-%d")
    hour = dt.hour
    
    recording_file = f"{RECORDINGS_PATH}/cam_{camera_id}/{date_str}/{hour:02d}.mp4"
    
    if not os.path.exists(recording_file):
        raise HTTPException(status_code=404, detail="Recording not found")
    
    # Criar path temporário no MediaMTX
    playback_path = f"playback_cam_{camera_id}_{int(dt.timestamp())}"
    
    async with httpx.AsyncClient() as client:
        config = {
            "source": f"file://{recording_file}",
            "sourceOnDemand": True,
            "record": False
        }
        
        resp = await client.post(
            f"{MEDIAMTX_API}/v3/config/paths/add/{playback_path}",
            json=config,
            auth=MEDIAMTX_AUTH
        )
        
        if resp.status_code in [200, 201, 409]:
            return {
                "success": True,
                "hls_url": f"/hls/{playback_path}/index.m3u8",
                "playback_path": playback_path
            }
        
        raise HTTPException(status_code=500, detail="Failed to start playback")

@app.delete("/playback/{playback_path}")
async def stop_playback(playback_path: str):
    """Remove stream de playback."""
    async with httpx.AsyncClient() as client:
        await client.delete(
            f"{MEDIAMTX_API}/v3/config/paths/delete/{playback_path}",
            auth=MEDIAMTX_AUTH
        )
    return {"success": True}
```

### 3.2 Criar Dockerfile

**Arquivo**: `services/playback/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install fastapi uvicorn httpx pydantic pydantic-settings

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006"]
```

### 3.3 Adicionar ao docker-compose.yml

```yaml
playback:
  build:
    context: ./services/playback
    dockerfile: Dockerfile
  container_name: gtvision_playback
  ports:
    - "8006:8006"
  volumes:
    - mediamtx_recordings:/recordings:ro
  depends_on:
    mediamtx:
      condition: service_healthy
  networks:
    - gtvision_network
  restart: unless-stopped
```

---

## CRITÉRIOS DE ACEITAÇÃO

- [ ] API retorna timeline correta
- [ ] Playback inicia em < 2s
- [ ] HLS é servido corretamente
- [ ] Player não percebe diferença (live vs gravação)
- [ ] Múltiplos playbacks simultâneos funcionam

---

## TESTES

### Teste 1: Timeline
```bash
curl http://localhost:8006/cameras/999/timeline?date=2026-02-05
```

**Resposta esperada**:
```json
{
  "segments": [
    {
      "start": "2026-02-05T00:00:00",
      "end": "2026-02-05T01:00:00",
      "file_path": "/recordings/cam_999/2026-02-05/00.mp4",
      "size_bytes": 1350000000,
      "duration_seconds": 3600
    },
    ...
  ]
}
```

### Teste 2: Iniciar Playback
```bash
curl -X POST http://localhost:8006/playback/start \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": 999,
    "start_time": "2026-02-05T15:30:00"
  }'
```

**Resposta esperada**:
```json
{
  "success": true,
  "hls_url": "/hls/playback_cam_999_1738771800/index.m3u8",
  "playback_path": "playback_cam_999_1738771800"
}
```

### Teste 3: Player Consome HLS
```html
<video id="video" controls></video>
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<script>
  const video = document.getElementById('video');
  const hls = new Hls();
  hls.loadSource('/hls/playback_cam_999_1738771800/index.m3u8');
  hls.attachMedia(video);
</script>
```

---

## PROBLEMAS ESPERADOS

### Problema 1: MediaMTX não encontra arquivo
**Sintoma**: 404 no HLS

**Debug**:
```bash
# Verificar se arquivo existe
ls -lh /recordings/cam_999/2026-02-05/15.mp4

# Verificar path no MediaMTX
curl http://localhost:9997/v3/paths/get/playback_cam_999_1738771800 \
  -u mediamtx_api_user:GtV!sionMed1aMTX$2025
```

**Solução**: Verificar montagem do volume

### Problema 2: Playback não inicia
**Sintoma**: HLS retorna erro

**Debug**:
```bash
# Verificar logs do MediaMTX
docker logs gtvision_mediamtx | grep "playback_cam_999"
```

**Solução**: Verificar formato do arquivo (deve ser fMP4)

---

## ENTREGÁVEIS

- [ ] Serviço de Playback funcional
- [ ] API de Timeline
- [ ] Testes de integração
- [ ] Documentação de API
