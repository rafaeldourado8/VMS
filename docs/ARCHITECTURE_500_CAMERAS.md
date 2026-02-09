# 🏗️ ARQUITETURA PARA 500 CÂMERAS

## Requisito
**500 câmeras por usuário** com gravação 24/7 e streaming ao vivo

---

## 📊 CÁLCULO DE RECURSOS

### Por 500 Câmeras
```
Bitrate: 2 Mbps/câmera
Armazenamento/dia: 10.8 TB
Armazenamento/7 dias: 75.6 TB
CPU necessária: 75 cores (gravação + streaming)
RAM necessária: 50 GB
Bandwidth: 1 Gbps (entrada) + 2 Gbps (saída para viewers)
```

---

## 🎯 ARQUITETURA PROPOSTA: KUBERNETES

### Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
│                   (Ingress NGINX)                       │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼───────┐  ┌───────▼────────┐
│  MediaMTX Pod  │  │ MediaMTX Pod │  │  MediaMTX Pod  │
│  (0-24 cams)   │  │ (25-49 cams) │  │ (50-74 cams)   │
│  2 CPU / 2GB   │  │ 2 CPU / 2GB  │  │  2 CPU / 2GB   │
└────────────────┘  └──────────────┘  └────────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼────────┐
                    │  MinIO/S3      │
                    │  (Storage)     │
                    │  100 TB        │
                    └────────────────┘
```

### Escalabilidade
- **20 Pods MediaMTX** (25 câmeras cada)
- **Auto-scaling**: Adiciona pod quando >20 câmeras/pod
- **Storage**: MinIO (S3-compatible) com 100 TB

---

## 💰 CUSTO ESTIMADO (AWS/Cloud)

### Opção 1: AWS
```
EC2 Instances:
- 20x c5.2xlarge (8 vCPU, 16GB): $3,400/mês
- 1x r5.4xlarge (DB): $960/mês

Storage:
- S3 Standard (100 TB): $2,300/mês
- S3 Glacier (archive): $400/mês

Bandwidth:
- 50 TB/mês saída: $4,500/mês

Total: ~$11,600/mês (~R$ 58,000/mês)
```

### Opção 2: Bare Metal (On-Premise)
```
Hardware (investimento inicial):
- 2x Servidor Dell R750 (64 cores, 256GB): $30,000
- Storage NAS 100TB: $15,000
- Switch 10Gbps: $3,000
Total: ~$48,000 (R$ 240,000)

Operacional:
- Energia: $500/mês
- Internet 1Gbps: $1,000/mês
- Manutenção: $500/mês
Total: ~$2,000/mês (R$ 10,000/mês)

ROI: 5 meses vs AWS
```

---

## 🚀 IMPLEMENTAÇÃO KUBERNETES

### 1. Helm Chart - MediaMTX

```yaml
# mediamtx-chart/values.yaml
replicaCount: 20

resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 1000m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 5
  maxReplicas: 30
  targetCPUUtilizationPercentage: 70

storage:
  class: "fast-ssd"
  size: 5Ti
  type: "minio"

config:
  maxCamerasPerPod: 25
  recordPath: "s3://recordings/%path/%Y-%m-%d/%H-%M-%S-%f.mp4"
```

### 2. Deployment

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mediamtx
spec:
  replicas: 20
  template:
    spec:
      containers:
      - name: mediamtx
        image: bluenviron/mediamtx:latest-ffmpeg
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
        env:
        - name: POD_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        volumeMounts:
        - name: recordings
          mountPath: /recordings
  volumeClaimTemplates:
  - metadata:
      name: recordings
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 5Ti
```

### 3. Service Discovery

```python
class MediaMTXRouter:
    """Roteia câmeras para pods disponíveis."""
    
    async def get_pod_for_camera(self, camera_id: int):
        # Consistente hashing
        pod_id = camera_id % 20  # 20 pods
        return f"mediamtx-{pod_id}.mediamtx-service:9997"
    
    async def provision_camera(self, camera_id: int, rtsp_url: str):
        pod_url = await self.get_pod_for_camera(camera_id)
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"http://{pod_url}/v3/config/paths/add/cam_{camera_id}",
                json={
                    "source": rtsp_url,
                    "record": True,
                    "recordPath": f"s3://recordings/cam_{camera_id}/%Y-%m-%d/%H-%M-%S-%f.mp4"
                }
            )
        return resp.status_code == 200
```

---

## 📦 ALTERNATIVA SIMPLES: Docker Swarm

### docker-compose.yml (Swarm Mode)

```yaml
version: '3.8'

services:
  mediamtx:
    image: bluenviron/mediamtx:latest-ffmpeg
    deploy:
      replicas: 20
      resources:
        limits:
          cpus: '2'
          memory: 2G
      placement:
        max_replicas_per_node: 5
    volumes:
      - recordings:/recordings
    networks:
      - vms_network

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: password
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: '4'
          memory: 8G

volumes:
  recordings:
    driver: local
    driver_opts:
      type: nfs
      o: addr=nas.local,rw
      device: ":/recordings"
  
  minio_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/storage

networks:
  vms_network:
    driver: overlay
```

---

## 🎯 ROADMAP DE IMPLEMENTAÇÃO

### Fase 1: MVP (0-50 câmeras) ✅ ATUAL
- Single MediaMTX instance
- Local storage
- Custo: ~$0 (on-premise)

### Fase 2: Crescimento (50-100 câmeras)
- 3-5 MediaMTX instances
- Docker Compose multi-instance
- NAS storage
- Custo: +$5,000 hardware

### Fase 3: Escala (100-200 câmeras)
- Docker Swarm (10 nodes)
- MinIO cluster
- Load balancer
- Custo: +$15,000 hardware

### Fase 4: Enterprise (200-500 câmeras)
- Kubernetes cluster
- S3/MinIO distributed
- CDN para HLS
- Auto-scaling
- Custo: $50,000 hardware OU $10,000/mês cloud

---

## 🔧 PRÓXIMOS PASSOS IMEDIATOS

### Para suportar 500 câmeras:

1. **Implementar Sharding** (próxima semana)
   ```python
   # Criar 20 instâncias MediaMTX
   # Rotear câmeras por hash: camera_id % 20
   ```

2. **Migrar Storage para MinIO** (2 semanas)
   ```bash
   # Instalar MinIO
   # Configurar recordPath para S3
   ```

3. **Implementar Load Balancer** (1 semana)
   ```nginx
   # HAProxy ou NGINX
   # Round-robin entre instâncias
   ```

4. **Kubernetes (opcional)** (1 mês)
   ```bash
   # Migrar para K8s
   # Auto-scaling configurado
   ```

---

## 💡 RECOMENDAÇÃO

**Para 500 câmeras:**

### Opção A: On-Premise (RECOMENDADO)
- **Hardware**: 2 servidores + NAS (R$ 240k)
- **Custo mensal**: R$ 10k
- **ROI**: 5 meses vs cloud
- **Controle total**

### Opção B: Hybrid Cloud
- **On-premise**: 200 câmeras principais
- **Cloud**: 300 câmeras overflow
- **Custo**: R$ 150k hardware + R$ 20k/mês cloud
- **Flexibilidade**

### Opção C: Full Cloud
- **AWS/Azure**: Kubernetes managed
- **Custo**: R$ 60k/mês
- **Zero manutenção**
- **Escalabilidade infinita**

---

## ✅ DECISÃO NECESSÁRIA

Qual caminho seguir?
1. **Implementar sharding agora** (suporta até 100 câmeras)
2. **Planejar Kubernetes** (suporta 500+ câmeras)
3. **Hybrid approach** (on-premise + cloud)
