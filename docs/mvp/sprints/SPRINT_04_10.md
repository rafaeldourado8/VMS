# 🎯 SPRINTS 4-10: DETALHAMENTO

## SPRINT 4: INTEGRAÇÃO FRONTEND

### Objetivo
Integrar Timeline e Playback no player React existente

### Tarefas
1. **Componente Timeline**
```tsx
// src/components/Timeline.tsx
interface TimelineProps {
  cameraId: number;
  date: string;
  onSegmentClick: (startTime: string) => void;
}

export function Timeline({ cameraId, date, onSegmentClick }: TimelineProps) {
  const [segments, setSegments] = useState([]);
  
  useEffect(() => {
    fetch(`/api/playback/cameras/${cameraId}/timeline?date=${date}`)
      .then(res => res.json())
      .then(data => setSegments(data.segments));
  }, [cameraId, date]);
  
  return (
    <div className="timeline">
      {segments.map(seg => (
        <div 
          key={seg.start}
          className="segment"
          onClick={() => onSegmentClick(seg.start)}
        >
          {new Date(seg.start).getHours()}:00
        </div>
      ))}
    </div>
  );
}
```

2. **Integração com Player**
```tsx
const [playbackMode, setPlaybackMode] = useState<'live' | 'recorded'>('live');
const [hlsUrl, setHlsUrl] = useState('');

const handlePlayback = async (startTime: string) => {
  const resp = await fetch('/api/playback/start', {
    method: 'POST',
    body: JSON.stringify({ camera_id: cameraId, start_time: startTime })
  });
  const data = await resp.json();
  setHlsUrl(data.hls_url);
  setPlaybackMode('recorded');
};
```

### Entregáveis
- [ ] Componente Timeline funcional
- [ ] Seletor de data
- [ ] Botão "Voltar ao Live"
- [ ] Indicador visual (live vs gravação)

---

## SPRINT 5: TESTES DE ESTRESSE

### Objetivo
Validar sistema com 12 câmeras simultâneas

### Cenários de Teste

#### Teste 1: 12 Câmeras Gravando
```bash
# Provisionar 12 câmeras
for i in {1..12}; do
  curl -X POST http://localhost:8001/cameras/provision \
    -d "{\"camera_id\": $i, \"rtsp_url\": \"rtsp://cam$i.local/stream\"}"
done

# Monitorar por 24h
watch -n 60 'docker stats gtvision_mediamtx'
```

#### Teste 2: Playback Simultâneo
```bash
# 5 usuários assistindo playback ao mesmo tempo
for i in {1..5}; do
  curl -X POST http://localhost:8006/playback/start \
    -d "{\"camera_id\": $i, \"start_time\": \"2026-02-05T15:00:00\"}" &
done
```

#### Teste 3: Restart Durante Gravação
```bash
# Restart às 15:30
docker restart gtvision_mediamtx

# Validar:
# - 15.mp4 existe (pode estar incompleto)
# - 16.mp4 é criado normalmente
```

#### Teste 4: Disco Cheio
```bash
# Simular disco cheio
dd if=/dev/zero of=/recordings/dummy.bin bs=1G count=100

# Verificar:
# - MediaMTX apaga arquivos antigos
# - Gravação continua
```

### Métricas
- CPU: < 80%
- RAM: < 1.5GB
- Disco I/O: < 100 MB/s
- Latência HLS: < 2s

---

## SPRINT 6: ORQUESTRAÇÃO DE NÓS

### Objetivo
Implementar sistema de alocação de câmeras em múltiplos nós

### Schema do Banco

```sql
-- Tabela de nós MediaMTX
CREATE TABLE media_nodes (
    id SERIAL PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,
    api_url VARCHAR(255) NOT NULL,
    hls_url VARCHAR(255) NOT NULL,
    max_cameras INT DEFAULT 12,
    current_cameras INT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active',
    disk_usage_percent FLOAT DEFAULT 0,
    cpu_usage_percent FLOAT DEFAULT 0,
    last_health_check TIMESTAMP DEFAULT NOW()
);

-- Tabela de mapeamento câmera → nó
CREATE TABLE camera_node_mapping (
    camera_id INT PRIMARY KEY,
    node_id INT REFERENCES media_nodes(id),
    assigned_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(camera_id)
);

-- Índices
CREATE INDEX idx_node_status ON media_nodes(status);
CREATE INDEX idx_node_load ON media_nodes(current_cameras);
```

### API de Orquestração

```python
# services/orchestrator/main.py
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

app = FastAPI()

def allocate_camera(camera_id: int) -> dict:
    """Aloca câmera no nó com menor carga."""
    with Session(engine) as session:
        # Busca nó disponível
        node = session.execute(
            select(MediaNode)
            .where(MediaNode.status == 'active')
            .where(MediaNode.current_cameras < MediaNode.max_cameras)
            .order_by(MediaNode.current_cameras)
        ).scalar_one_or_none()
        
        if not node:
            raise HTTPException(503, "No available nodes")
        
        # Atualiza contador
        node.current_cameras += 1
        
        # Cria mapeamento
        mapping = CameraNodeMapping(
            camera_id=camera_id,
            node_id=node.id
        )
        session.add(mapping)
        session.commit()
        
        return {
            "node_id": node.id,
            "api_url": node.api_url,
            "hls_url": node.hls_url
        }

@app.post("/cameras/{camera_id}/allocate")
def allocate(camera_id: int):
    return allocate_camera(camera_id)

@app.get("/nodes/status")
def nodes_status():
    with Session(engine) as session:
        nodes = session.execute(select(MediaNode)).scalars().all()
        return [
            {
                "id": n.id,
                "hostname": n.hostname,
                "cameras": n.current_cameras,
                "max": n.max_cameras,
                "status": n.status
            }
            for n in nodes
        ]
```

---

## SPRINT 7: DEPLOY MULTI-NÓ LOCAL

### docker-compose.multi-node.yml

```yaml
services:
  mediamtx_node_1:
    image: bluenviron/mediamtx:latest-ffmpeg
    container_name: mediamtx_node_1
    ports:
      - "8888:8888"
      - "9997:9997"
    volumes:
      - ./mediamtx.yml:/mediamtx.yml:ro
      - mediamtx_recordings_1:/recordings
    networks:
      - gtvision_network

  mediamtx_node_2:
    image: bluenviron/mediamtx:latest-ffmpeg
    container_name: mediamtx_node_2
    ports:
      - "8889:8888"
      - "9998:9997"
    volumes:
      - ./mediamtx.yml:/mediamtx.yml:ro
      - mediamtx_recordings_2:/recordings
    networks:
      - gtvision_network

  mediamtx_node_3:
    image: bluenviron/mediamtx:latest-ffmpeg
    container_name: mediamtx_node_3
    ports:
      - "8890:8888"
      - "9999:9997"
    volumes:
      - ./mediamtx.yml:/mediamtx.yml:ro
      - mediamtx_recordings_3:/recordings
    networks:
      - gtvision_network

  orchestrator:
    build: ./services/orchestrator
    container_name: gtvision_orchestrator
    ports:
      - "8007:8007"
    environment:
      DATABASE_URL: postgresql://user:pass@postgres/gtvision
    depends_on:
      - mediamtx_node_1
      - mediamtx_node_2
      - mediamtx_node_3
    networks:
      - gtvision_network

volumes:
  mediamtx_recordings_1:
  mediamtx_recordings_2:
  mediamtx_recordings_3:
```

### Teste de Alocação

```bash
# Provisionar 36 câmeras (12 por nó)
for i in {1..36}; do
  curl -X POST http://localhost:8007/cameras/$i/allocate
done

# Verificar distribuição
curl http://localhost:8007/nodes/status

# Resposta esperada:
# [
#   {"id": 1, "cameras": 12, "max": 12},
#   {"id": 2, "cameras": 12, "max": 12},
#   {"id": 3, "cameras": 12, "max": 12}
# ]
```

---

## SPRINT 8: FAILOVER E RECUPERAÇÃO

### Health Check Service

```python
# services/orchestrator/health_check.py
import asyncio
import httpx
from datetime import datetime

async def check_node_health(node: MediaNode):
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{node.api_url}/v3/config/global/get")
            
            if resp.status_code == 200:
                node.status = 'active'
                node.last_health_check = datetime.now()
            else:
                node.status = 'degraded'
    except:
        node.status = 'offline'
        await handle_node_failure(node)

async def handle_node_failure(node: MediaNode):
    """Redistribui câmeras de nó offline."""
    cameras = get_cameras_on_node(node.id)
    
    for camera in cameras:
        # Aloca em novo nó
        new_node = allocate_camera(camera.id)
        
        # Reprovisiona câmera
        await provision_camera_on_node(camera, new_node)
        
        print(f"Camera {camera.id} migrated: node {node.id} → {new_node.id}")

async def health_check_loop():
    while True:
        nodes = get_all_nodes()
        await asyncio.gather(*[check_node_health(n) for n in nodes])
        await asyncio.sleep(30)
```

### Teste de Failover

```bash
# Parar nó 2
docker stop mediamtx_node_2

# Aguardar 30s (health check)
sleep 30

# Verificar redistribuição
curl http://localhost:8007/nodes/status

# Câmeras do nó 2 devem estar em nó 1 ou 3
```

---

## SPRINT 9: BALANCEAMENTO DE CARGA

### Algoritmo Avançado

```python
def allocate_camera_smart(camera_id: int, bitrate_mbps: float = 3.0):
    """Aloca considerando CPU, disco e bitrate."""
    nodes = get_active_nodes()
    
    # Calcula score para cada nó
    scores = []
    for node in nodes:
        # Fatores de carga
        camera_load = node.current_cameras / node.max_cameras
        cpu_load = node.cpu_usage_percent / 100
        disk_load = node.disk_usage_percent / 100
        
        # Score ponderado (menor é melhor)
        score = (
            camera_load * 0.5 +
            cpu_load * 0.3 +
            disk_load * 0.2
        )
        
        scores.append((node, score))
    
    # Seleciona nó com menor score
    best_node = min(scores, key=lambda x: x[1])[0]
    
    return best_node
```

---

## SPRINT 10: VALIDAÇÃO 120 CÂMERAS

### Setup Completo

```bash
# Deploy 10 nós
docker-compose -f docker-compose.10-nodes.yml up -d

# Provisionar 120 câmeras
for i in {1..120}; do
  curl -X POST http://localhost:8007/cameras/$i/allocate
  curl -X POST http://localhost:8001/cameras/provision \
    -d "{\"camera_id\": $i, \"rtsp_url\": \"rtsp://cam$i/stream\"}"
done

# Monitorar por 7 dias
```

### Métricas de Sucesso
- [ ] 120 câmeras gravando simultaneamente
- [ ] Distribuição uniforme (12 câmeras/nó)
- [ ] CPU < 70% em todos os nós
- [ ] Disco crescendo linearmente
- [ ] Zero perda de gravações
- [ ] Playback funcional em todas as câmeras
