# 📊 ANÁLISE DE CARGA - MediaMTX

## Cenário Atual
- **11 câmeras LPR** (Camapuã + Naviraí)
- **1 instância MediaMTX**
- **Gravação 24/7** (168h retenção)

---

## 🧮 CÁLCULO DE RECURSOS

### Por Câmera (estimativa)
```
Bitrate médio: 2 Mbps (H.264)
Armazenamento/hora: ~900 MB
Armazenamento/dia: ~21.6 GB
Armazenamento/7 dias: ~151 GB
```

### 11 Câmeras
```
Bitrate total: 22 Mbps
Armazenamento/dia: 237 GB
Armazenamento/7 dias: 1.66 TB
CPU: ~1.5 cores (transcoding desabilitado)
RAM: ~1.5 GB
```

### 50 Câmeras (futuro)
```
Bitrate total: 100 Mbps
Armazenamento/dia: 1.08 TB
Armazenamento/7 dias: 7.56 TB
CPU: ~6 cores
RAM: ~6 GB
```

---

## ⚠️ GARGALOS IDENTIFICADOS

### 1. Single Point of Failure
- 1 instância MediaMTX = se crashar, TODAS as câmeras caem
- Sem redundância

### 2. Limite de Recursos
- MediaMTX atual: 2.5 CPU / 2GB RAM
- Limite teórico: ~40-50 câmeras por instância

### 3. I/O de Disco
- Gravação simultânea de 11 streams = alta carga I/O
- Volume único = bottleneck

---

## 🏗️ ARQUITETURA PROPOSTA: MULTI-INSTÂNCIA

### Opção 1: Sharding por Região (RECOMENDADO)
```
┌─────────────────────────────────────────┐
│         HAProxy / Load Balancer         │
└─────────────────────────────────────────┘
           │                    │
    ┌──────┴──────┐      ┌─────┴──────┐
    │  MediaMTX 1 │      │ MediaMTX 2 │
    │  (Camapuã)  │      │ (Naviraí)  │
    │  5 câmeras  │      │  6 câmeras │
    └─────────────┘      └────────────┘
         │                      │
    ┌────┴─────┐          ┌────┴─────┐
    │ Volume 1 │          │ Volume 2 │
    │  840 GB  │          │  1 TB    │
    └──────────┘          └──────────┘
```

**Vantagens:**
- ✅ Isolamento geográfico
- ✅ Falha em 1 região não afeta outra
- ✅ Distribuição natural de carga
- ✅ Fácil adicionar novas regiões

**Desvantagens:**
- ❌ Mais complexo gerenciar
- ❌ Precisa load balancer

---

### Opção 2: Sharding por Capacidade
```
MediaMTX 1: cam_1  até cam_25  (25 câmeras)
MediaMTX 2: cam_26 até cam_50  (25 câmeras)
MediaMTX 3: cam_51 até cam_75  (25 câmeras)
```

**Vantagens:**
- ✅ Simples de implementar
- ✅ Balanceamento automático
- ✅ Escalável horizontalmente

**Desvantagens:**
- ❌ Sem isolamento lógico
- ❌ Dificulta troubleshooting

---

### Opção 3: Active-Passive (Alta Disponibilidade)
```
┌──────────────┐      ┌──────────────┐
│  MediaMTX 1  │ ───► │  MediaMTX 2  │
│   (Active)   │      │  (Standby)   │
│ 11 câmeras   │      │  0 câmeras   │
└──────────────┘      └──────────────┘
       │                      │
       └──────────┬───────────┘
              ┌───┴────┐
              │ Volume │
              │ Shared │
              └────────┘
```

**Vantagens:**
- ✅ Alta disponibilidade
- ✅ Failover automático
- ✅ Sem perda de gravações

**Desvantagens:**
- ❌ Recursos ociosos (standby)
- ❌ Complexo implementar failover

---

## 🎯 RECOMENDAÇÃO: OPÇÃO 1 (Sharding por Região)

### Implementação

**docker-compose.yml**
```yaml
services:
  # MediaMTX Camapuã
  mediamtx_camapua:
    image: bluenviron/mediamtx:latest-ffmpeg
    container_name: gtvision_mediamtx_camapua
    ports:
      - "8888:8888"   # HLS
      - "9997:9997"   # API
    volumes:
      - ./mediamtx_camapua.yml:/mediamtx.yml:ro
      - mediamtx_recordings_camapua:/recordings
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 1G
    restart: unless-stopped

  # MediaMTX Naviraí
  mediamtx_navirai:
    image: bluenviron/mediamtx:latest-ffmpeg
    container_name: gtvision_mediamtx_navirai
    ports:
      - "8889:8888"   # HLS
      - "9998:9997"   # API
    volumes:
      - ./mediamtx_navirai.yml:/mediamtx.yml:ro
      - mediamtx_recordings_navirai:/recordings
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 1G
    restart: unless-stopped

volumes:
  mediamtx_recordings_camapua:
  mediamtx_recordings_navirai:
```

**Streaming Service (atualizar)**
```python
MEDIAMTX_INSTANCES = {
    "camapua": {
        "api_url": "http://mediamtx_camapua:9997",
        "hls_url": "http://mediamtx_camapua:8888",
        "camera_range": range(10, 20)  # cam_10 a cam_19
    },
    "navirai": {
        "api_url": "http://mediamtx_navirai:9997",
        "hls_url": "http://mediamtx_navirai:8888",
        "camera_range": range(20, 30)  # cam_20 a cam_29
    }
}

def get_mediamtx_instance(camera_id: int):
    for region, config in MEDIAMTX_INSTANCES.items():
        if camera_id in config["camera_range"]:
            return config
    return MEDIAMTX_INSTANCES["camapua"]  # default
```

---

## 🧪 TESTES DE CARGA

### Teste 1: 10 Câmeras Simultâneas
```bash
# Script de teste
for i in {10..19}; do
  curl -X POST http://localhost:8001/cameras/provision \
    -H "Content-Type: application/json" \
    -d "{\"camera_id\":$i,\"rtsp_url\":\"rtsp://...\",\"name\":\"Test $i\",\"enabled\":true,\"on_demand\":false}" &
done
wait

# Monitorar recursos
docker stats gtvision_mediamtx --no-stream
```

**Métricas esperadas:**
- CPU: 60-80%
- RAM: 800 MB - 1.2 GB
- Disk I/O: 20-30 MB/s

---

### Teste 2: Simular 10 Dias de Gravação
```bash
# Criar estrutura de 10 dias
for day in {0..10}; do
  date_str=$(date -d "$day days ago" +%Y-%m-%d 2>/dev/null || date -v-${day}d +%Y-%m-%d)
  
  for cam in {10..19}; do
    mkdir -p /recordings/cam_$cam/$date_str
    
    # Criar 24 arquivos de 1 hora (900 MB cada)
    for hour in {00..23}; do
      dd if=/dev/zero of=/recordings/cam_$cam/$date_str/$hour-00-00-000001.mp4 bs=1M count=900
    done
  done
done

# Verificar espaço
du -sh /recordings/
# Esperado: ~2.4 TB (10 câmeras × 10 dias × 21.6 GB)
```

---

### Teste 3: Stress Test - Viewers Simultâneos
```bash
# 50 viewers simultâneos em 10 câmeras
for i in {1..50}; do
  cam_id=$((10 + RANDOM % 10))
  ffplay -loglevel quiet http://localhost:8001/hls/cam_$cam_id/index.m3u8 &
done

# Monitorar
docker stats gtvision_mediamtx
```

**Limite esperado:**
- ~100 viewers simultâneos por instância
- CPU: 90-100%
- RAM: 1.5-2 GB

---

### Teste 4: Crash Recovery
```bash
# Simular crash
docker kill -s SIGKILL gtvision_mediamtx

# Verificar tempo de recovery
time docker ps | grep mediamtx

# Verificar se câmeras foram reprovisionadas
curl http://localhost:9997/v3/paths/list -u user:pass
```

**SLA esperado:**
- Recovery time: < 30s
- Reprovisioning: < 2 min

---

## 📈 ROADMAP DE ESCALABILIDADE

### Fase 1: Atual (11 câmeras)
- ✅ 1 instância MediaMTX
- ✅ Gravação 24/7
- ✅ Monitor de crashes

### Fase 2: Curto Prazo (até 25 câmeras)
- 🔄 2 instâncias MediaMTX (sharding por região)
- 🔄 Load balancer (HAProxy)
- 🔄 Volumes separados

### Fase 3: Médio Prazo (até 50 câmeras)
- ⏳ 3-4 instâncias MediaMTX
- ⏳ Auto-scaling baseado em carga
- ⏳ Storage distribuído (NFS/Ceph)

### Fase 4: Longo Prazo (100+ câmeras)
- ⏳ Kubernetes cluster
- ⏳ Object storage (MinIO/S3)
- ⏳ CDN para HLS

---

## 💰 CUSTO vs BENEFÍCIO

### Single Instance (atual)
- **Custo**: Baixo
- **Capacidade**: 25-30 câmeras
- **Risco**: Alto (SPOF)

### Multi-Instance (proposto)
- **Custo**: +30% recursos
- **Capacidade**: 50-60 câmeras
- **Risco**: Baixo (redundância)

### Kubernetes (futuro)
- **Custo**: +100% recursos
- **Capacidade**: Ilimitado
- **Risco**: Muito baixo

---

## 🎬 PRÓXIMOS PASSOS

1. ✅ Executar testes de carga (10 câmeras)
2. ⏳ Implementar sharding por região
3. ⏳ Configurar HAProxy
4. ⏳ Testar failover
5. ⏳ Documentar runbook operacional
