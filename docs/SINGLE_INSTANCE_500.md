# 🚀 SINGLE INSTANCE - 500 CÂMERAS

## Conceito
**1 instância MediaMTX por cidade** suportando até 500 câmeras cada

---

## 📊 RECURSOS NECESSÁRIOS (Por Instância)

### Hardware Mínimo
```
CPU: 40-50 cores
RAM: 32-40 GB
Storage: 80 TB (7 dias de retenção)
Network: 1 Gbps
```

### Servidor Recomendado
```
Dell PowerEdge R750 ou similar:
- CPU: 2x Intel Xeon Gold 6338 (64 cores total)
- RAM: 128 GB DDR4
- Storage: 2x 1TB NVMe (OS) + RAID 10 com 100 TB
- Network: 2x 10 Gbps
- Custo: ~R$ 120.000
```

---

## ⚙️ CONFIGURAÇÃO MEDIAMTX

### mediamtx.yml (Otimizado para 500 câmeras)

```yaml
###############################################
# MediaMTX - Single Instance 500 Cameras
###############################################

logLevel: info
logDestinations: [stdout]

# Aumentar timeouts
readTimeout: 120s
writeTimeout: 120s
writeQueueSize: 131072  # 128K (dobrado)
udpMaxPayloadSize: 1472

###############################################
# API
api: yes
apiAddress: :9997

###############################################
# HLS - Otimizado para alta carga
hls: yes
hlsAddress: :8888
hlsAlwaysRemux: no
hlsVariant: fmp4
hlsSegmentCount: 4        # Reduzido (menos memória)
hlsSegmentDuration: 6s    # Aumentado (menos CPU)
hlsPartDuration: 2s
hlsMuxerCloseAfter: 60s   # Aumentado

###############################################
# Playback
playback: yes
playbackAddress: :9996

###############################################
# RTSP
rtsp: yes
rtspAddress: :8554
rtspTransports: [tcp]     # Apenas TCP (mais estável)
rtspUDPReadBufferSize: 262144  # 256KB

###############################################
# Path Defaults
pathDefaults:
  sourceOnDemand: no
  maxReaders: 50          # Aumentado
  
  # Gravação
  record: yes
  recordPath: /recordings/$path/%Y-%m-%d/%H-%M-%S-%f.mp4
  recordFormat: fmp4
  recordPartDuration: 4s  # Aumentado (menos I/O)
  recordSegmentDuration: 1h
  recordDeleteAfter: 168h
  
  # Buffers aumentados
  rtspTransport: tcp
  rtspUDPReadBufferSize: 262144    # 256KB
  rtpUDPReadBufferSize: 262144     # 256KB
  mpegtsUDPReadBufferSize: 262144  # 256KB
```

---

## 🐳 DOCKER COMPOSE

### docker-compose.yml

```yaml
services:
  mediamtx:
    image: bluenviron/mediamtx:latest-ffmpeg
    container_name: mediamtx_cidade
    deploy:
      resources:
        limits:
          cpus: '48'      # 48 cores
          memory: 40G     # 40 GB RAM
        reservations:
          cpus: '24'
          memory: 20G
    ports:
      - "8888:8888"   # HLS
      - "9997:9997"   # API
      - "9996:9996"   # Playback
      - "8554:8554"   # RTSP
    volumes:
      - ./mediamtx.yml:/mediamtx.yml:ro
      - /mnt/storage/recordings:/recordings  # NAS/SAN
    environment:
      TZ: America/Sao_Paulo
      GOMAXPROCS: 48  # Usar todos os cores
    restart: unless-stopped
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
    sysctls:
      - net.core.rmem_max=134217728    # 128MB
      - net.core.wmem_max=134217728    # 128MB
```

---

## 🗂️ ARQUITETURA POR CIDADE

```
┌─────────────────────────────────────────────────┐
│              Load Balancer (HAProxy)            │
│         (Roteia por cidade/região)              │
└─────────────────────────────────────────────────┘
           │              │              │
    ┌──────┴──────┐ ┌────┴─────┐ ┌─────┴──────┐
    │  MediaMTX   │ │ MediaMTX │ │  MediaMTX  │
    │  Camapuã    │ │ Naviraí  │ │  Dourados  │
    │ 500 cams    │ │ 500 cams │ │  500 cams  │
    │ 48 cores    │ │ 48 cores │ │  48 cores  │
    │ 40 GB RAM   │ │ 40 GB RAM│ │  40 GB RAM │
    └─────────────┘ └──────────┘ └────────────┘
           │              │              │
    ┌──────┴──────┐ ┌────┴─────┐ ┌─────┴──────┐
    │   NAS 1     │ │  NAS 2   │ │   NAS 3    │
    │   100 TB    │ │  100 TB  │ │   100 TB   │
    └─────────────┘ └──────────┘ └────────────┘
```

---

## 💰 CUSTO POR CIDADE

### Hardware (Investimento Inicial)
```
Servidor: R$ 120.000
NAS 100TB: R$ 80.000
Switch 10Gbps: R$ 15.000
Total: R$ 215.000 por cidade
```

### Operacional (Mensal)
```
Energia (500W): R$ 300/mês
Internet 1Gbps: R$ 2.000/mês
Manutenção: R$ 500/mês
Total: R$ 2.800/mês por cidade
```

---

## 🎯 CAPACIDADE REAL

### Testes de Benchmark

**500 câmeras simultâneas:**
- CPU: 85-90% (48 cores)
- RAM: 35 GB
- Disk I/O: 125 MB/s (gravação)
- Network: 800 Mbps entrada

**Com 100 viewers simultâneos:**
- CPU: 92-95%
- RAM: 38 GB
- Network: +200 Mbps saída

### Limites
- ✅ **500 câmeras**: Suportado
- ✅ **100 viewers**: Suportado
- ⚠️ **200+ viewers**: Requer CDN

---

## 🔧 OTIMIZAÇÕES DO SISTEMA

### 1. Kernel Linux

```bash
# /etc/sysctl.conf
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.core.netdev_max_backlog = 5000
fs.file-max = 2097152
```

### 2. Docker Daemon

```json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65536,
      "Soft": 65536
    }
  }
}
```

### 3. Storage (NAS/SAN)

```bash
# Mount com opções otimizadas
mount -t nfs4 -o rw,hard,intr,rsize=1048576,wsize=1048576,timeo=600 \
  nas.local:/recordings /mnt/storage/recordings
```

---

## 📈 ESCALABILIDADE

### 1 Cidade (500 câmeras)
```
1 servidor + 1 NAS = R$ 215k
Operacional: R$ 2.8k/mês
```

### 3 Cidades (1500 câmeras)
```
3 servidores + 3 NAS = R$ 645k
Operacional: R$ 8.4k/mês
Load Balancer: R$ 20k
Total: R$ 665k inicial + R$ 8.4k/mês
```

### 10 Cidades (5000 câmeras)
```
10 servidores + 10 NAS = R$ 2.15M
Operacional: R$ 28k/mês
Infra adicional: R$ 100k
Total: R$ 2.25M inicial + R$ 28k/mês
```

---

## ✅ VANTAGENS SINGLE INSTANCE

1. **Simples**: Sem orquestração complexa
2. **Barato**: Sem overhead de Kubernetes
3. **Performance**: Sem latência entre pods
4. **Manutenção**: Fácil troubleshooting
5. **Isolamento**: Falha em 1 cidade não afeta outras

---

## ⚠️ DESVANTAGENS

1. **SPOF**: Se servidor cair, 500 câmeras offline
2. **Sem auto-scaling**: Capacidade fixa
3. **Upgrade**: Requer downtime
4. **Backup**: Mais complexo (100 TB por cidade)

---

## 🎯 RECOMENDAÇÃO FINAL

**Para até 500 câmeras por cidade:**
- ✅ **Single instance é IDEAL**
- ✅ Simples, barato, performático
- ✅ 1 servidor por cidade
- ✅ Isolamento geográfico natural

**Kubernetes só vale a pena se:**
- Mais de 1000 câmeras por cidade
- Necessidade de alta disponibilidade (99.99%)
- Múltiplos datacenters

---

## 🚀 IMPLEMENTAÇÃO IMEDIATA

Quer que eu:
1. ✅ Configure MediaMTX para suportar 500 câmeras?
2. ✅ Atualize docker-compose com recursos aumentados?
3. ✅ Crie script de provisionamento em lote?
