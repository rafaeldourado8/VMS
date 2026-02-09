# 📊 CAPACIDADE DO SISTEMA ATUAL

## Hardware Alocado (Docker Limits)

### MediaMTX
- **CPU**: 3.0 cores (limite) / 1.5 cores (reservado)
- **RAM**: 3 GB (limite) / 1 GB (reservado)
- **Disco**: Ilimitado (volume Docker)

### Streaming Service
- **CPU**: 1.5 cores (limite) / 0.5 cores (reservado)
- **RAM**: 1 GB (limite) / 256 MB (reservado)

---

## 🎥 CAPACIDADE DE CÂMERAS

### Cálculo por Recursos

**CPU (gargalo principal):**
```
Por câmera (gravação 24/7):
- Recepção RTSP: ~0.05 cores
- Gravação fMP4: ~0.05 cores
- HLS muxing: ~0.05 cores (quando há viewers)
Total: ~0.15 cores/câmera (com viewers)

Capacidade teórica:
3.0 cores / 0.15 = 20 câmeras (com viewers ativos)
3.0 cores / 0.10 = 30 câmeras (só gravação, sem viewers)
```

**RAM:**
```
Por câmera:
- Buffers RTSP: ~50 MB
- Gravação: ~30 MB
- HLS cache: ~20 MB (quando há viewers)
Total: ~100 MB/câmera (com viewers)

Capacidade teórica:
3 GB / 100 MB = 30 câmeras (com viewers)
3 GB / 80 MB = 37 câmeras (só gravação)
```

**Disco I/O:**
```
Por câmera (2 Mbps):
- Gravação: ~250 KB/s = 0.25 MB/s

10 câmeras: 2.5 MB/s
20 câmeras: 5 MB/s
30 câmeras: 7.5 MB/s

Limite SSD moderno: ~500 MB/s
Capacidade teórica: 2000 câmeras (não é gargalo)
```

### ✅ CAPACIDADE REAL (Conservadora)

| Cenário | Câmeras | CPU | RAM | Observação |
|---------|---------|-----|-----|------------|
| **Atual (9 câmeras)** | 9 | 30% | 900 MB | ✅ Confortável |
| **Recomendado** | **15-20** | 60-70% | 1.5-2 GB | ✅ Ideal |
| **Máximo (sem viewers)** | 25-30 | 90% | 2.5 GB | ⚠️ Limite |
| **Máximo (com viewers)** | 15-20 | 90% | 2.5 GB | ⚠️ Limite |

---

## 👥 CAPACIDADE DE VIEWERS (Players Simultâneos)

### Cálculo por Recursos

**CPU (HLS muxing):**
```
Por viewer ativo:
- HLS muxing: ~0.02 cores (compartilhado entre viewers da mesma câmera)
- Segmentação: ~0.01 cores

10 viewers (1 por câmera): ~0.3 cores
50 viewers (5 por câmera): ~1.0 cores
100 viewers (10 por câmera): ~1.5 cores

Capacidade teórica:
3.0 cores - 1.5 cores (câmeras) = 1.5 cores disponíveis
1.5 cores / 0.015 = 100 viewers simultâneos
```

**RAM (HLS cache):**
```
Por viewer:
- HLS segments cache: ~10 MB (compartilhado)
- Connection overhead: ~5 MB

10 viewers: ~150 MB
50 viewers: ~500 MB
100 viewers: ~800 MB

Capacidade teórica:
3 GB - 1.5 GB (câmeras) = 1.5 GB disponível
1.5 GB / 15 MB = 100 viewers
```

**Rede (Bandwidth):**
```
Por viewer (HLS):
- Bitrate: ~2 Mbps = 0.25 MB/s

10 viewers: 2.5 MB/s = 20 Mbps
50 viewers: 12.5 MB/s = 100 Mbps
100 viewers: 25 MB/s = 200 Mbps

Limite rede 1 Gbps: 500 viewers (não é gargalo)
```

### ✅ CAPACIDADE REAL (Conservadora)

| Cenário | Viewers | CPU | RAM | Bandwidth | Observação |
|---------|---------|-----|-----|-----------|------------|
| **Atual (0-5)** | 5 | +5% | +50 MB | 10 Mbps | ✅ Confortável |
| **Recomendado** | **30-50** | +30% | +500 MB | 100 Mbps | ✅ Ideal |
| **Máximo** | **80-100** | +50% | +1 GB | 200 Mbps | ⚠️ Limite |

---

## 📈 CENÁRIOS COMBINADOS

### Cenário 1: Operação Normal
```
15 câmeras gravando 24/7
20 viewers simultâneos (média 1-2 por câmera)

CPU: 1.5 cores (câmeras) + 0.3 cores (viewers) = 1.8 cores (60%)
RAM: 1.5 GB (câmeras) + 300 MB (viewers) = 1.8 GB (60%)
Disco: 3.75 MB/s gravação
Rede: 40 Mbps saída

Status: ✅ CONFORTÁVEL
```

### Cenário 2: Pico de Acesso
```
15 câmeras gravando 24/7
50 viewers simultâneos (média 3-4 por câmera)

CPU: 1.5 cores (câmeras) + 0.75 cores (viewers) = 2.25 cores (75%)
RAM: 1.5 GB (câmeras) + 750 MB (viewers) = 2.25 GB (75%)
Disco: 3.75 MB/s gravação
Rede: 100 Mbps saída

Status: ✅ ACEITÁVEL
```

### Cenário 3: Máximo Teórico
```
20 câmeras gravando 24/7
80 viewers simultâneos (média 4 por câmera)

CPU: 2.0 cores (câmeras) + 1.0 cores (viewers) = 3.0 cores (100%)
RAM: 2.0 GB (câmeras) + 1.0 GB (viewers) = 3.0 GB (100%)
Disco: 5 MB/s gravação
Rede: 160 Mbps saída

Status: ⚠️ LIMITE MÁXIMO
```

---

## 🚨 SINAIS DE SOBRECARGA

### CPU
- ❌ Drift frequente (>10/hora por câmera)
- ❌ Perda de pacotes RTP (>1000/min)
- ❌ HLS com buffering constante
- ❌ Latência >5s no live stream

### RAM
- ❌ OOM kills (container reiniciando)
- ❌ Swap usage alto
- ❌ Gravações corrompidas

### Disco
- ❌ Gravações com gaps
- ❌ Arquivos incompletos
- ❌ I/O wait alto

---

## 📊 RESUMO EXECUTIVO

### ✅ CAPACIDADE ATUAL (Single Instance)

| Métrica | Valor | Observação |
|---------|-------|------------|
| **Câmeras (gravação 24/7)** | **15-20** | Recomendado: 15 |
| **Câmeras (máximo)** | **25-30** | Sem viewers |
| **Viewers simultâneos** | **50-80** | Com 15 câmeras |
| **Viewers máximo** | **100** | Limite teórico |
| **Armazenamento (7 dias)** | **2.5 TB** | 15 câmeras |

### 🎯 RECOMENDAÇÃO OPERACIONAL

**Para 11 câmeras atuais:**
- ✅ Sistema está em **40% de capacidade**
- ✅ Suporta até **60 viewers simultâneos**
- ✅ Pode adicionar **4-9 câmeras** sem upgrade

**Para escalar além de 20 câmeras:**
- 🔄 Implementar **multi-instância** (2-3 MediaMTX)
- 🔄 Load balancer (HAProxy)
- 🔄 Storage distribuído

**Para escalar além de 50 câmeras:**
- 🔄 Kubernetes cluster
- 🔄 Object storage (MinIO/S3)
- 🔄 CDN para HLS

---

## 🧪 TESTE DE CARGA REALIZADO

**Resultado:**
- ✅ 9/11 câmeras provisionadas com sucesso
- ⚠️ 2 falhas por timeout de rede (não por capacidade)
- ✅ CPU: ~30% (confortável)
- ✅ RAM: ~900 MB (confortável)

**Conclusão:**
Sistema atual suporta **15-20 câmeras** com folga para crescimento.
