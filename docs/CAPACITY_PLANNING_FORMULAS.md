# 📊 Fórmulas de Planejamento de Capacidade - VMS

## 📹 1. STREAMING (HLS)

### Banda por Câmera
```
Bitrate_Camera = Resolução × FPS × Compression_Ratio

Exemplos:
- 1080p @ 30fps: 1920×1080×30×0.1 = 6,220,800 bits/s ≈ 6 Mbps
- 720p @ 15fps:  1280×720×15×0.1 = 1,382,400 bits/s ≈ 1.4 Mbps
```

### Banda Total Streaming
```
Banda_Total = N_Cameras × Bitrate_Camera × N_Viewers

Exemplo: 20 câmeras × 6 Mbps × 5 viewers = 600 Mbps
```

### Banda com Cache (10s)
```
Banda_Real = Banda_Total × Cache_Miss_Rate

Cache_Miss_Rate = 1 / (Viewing_Time / Cache_Duration)

Exemplo: 
- Viewing_Time = 60s
- Cache_Duration = 10s
- Cache_Miss_Rate = 1 / (60/10) = 16.67%
- Banda_Real = 600 Mbps × 0.1667 ≈ 100 Mbps
```

### Custo Banda AWS
```
Custo_Banda = (Banda_Real × Uptime × Days) / 8 / 1024 × Price_per_GB

Exemplo:
- 100 Mbps × 86400s × 30 dias / 8 / 1024 = 31,640 GB
- 31,640 GB × $0.09/GB = $2,847/mês
```

---

## 🤖 2. DETECÇÃO (YOLO + OCR)

### FPS Processamento
```
FPS_Real = FPS_Camera / Frame_Skip

Exemplo: 30 FPS / 3 = 10 FPS processados
```

### Frames por Dia
```
Frames_Day = N_Cameras × FPS_Real × 86400

Exemplo: 20 câmeras × 10 FPS × 86400 = 17,280,000 frames/dia
```

### Tempo Processamento
```
Processing_Time = Frames_Day × Time_per_Frame

Exemplo: 17,280,000 × 0.1s = 1,728,000s = 480 horas CPU
```

### CPU Necessária
```
CPU_Cores = Processing_Time / 86400

Exemplo: 480h / 24h = 20 cores
```

### Custo CPU AWS
```
Custo_CPU = CPU_Cores × Hours × Price_per_Hour

Exemplo: 20 cores × 720h × $0.0416 = $599/mês
```

---

## 💾 3. ARMAZENAMENTO (GRAVAÇÃO)

### Tamanho por Câmera
```
Size_per_Camera = Bitrate × Retention_Days × 86400 / 8

Exemplo (7 dias):
- 6 Mbps × 7 dias × 86400s / 8 = 453,600 MB ≈ 443 GB
```

### Armazenamento Total
```
Storage_Total = N_Cameras × Size_per_Camera

Exemplo: 20 câmeras × 443 GB = 8,860 GB ≈ 8.65 TB
```

### Custo Storage AWS S3
```
Custo_Storage = Storage_Total × Price_per_GB

Exemplo: 8,860 GB × $0.023/GB = $204/mês
```

---

## 👥 4. USUÁRIOS E TRÁFEGO

### DAU (Daily Active Users)
```
DAU = Total_Users × Activity_Rate

Exemplo: 100 users × 0.3 = 30 DAU
```

### RPS (Requests Per Second)
```
RPS = (DAU × Requests_per_Session × Sessions_per_Day) / 86400

Exemplo: (30 × 50 × 3) / 86400 = 0.052 RPS
```

### RPD (Requests Per Day)
```
RPD = DAU × Requests_per_Session × Sessions_per_Day

Exemplo: 30 × 50 × 3 = 4,500 RPD
```

### Concurrent Users
```
Concurrent_Users = DAU × Peak_Ratio × Avg_Session_Time / 86400

Exemplo: 30 × 0.2 × 1800 / 86400 = 0.125 ≈ 1 usuário simultâneo
```

---

## 🗄️ 5. BANCO DE DADOS

### Detecções por Dia
```
Detections_Day = N_Cameras × Detection_Rate × 86400

Exemplo: 20 câmeras × 0.1 det/s × 86400 = 172,800 detecções/dia
```

### Tamanho Banco (Detecções)
```
DB_Size = Detections_Day × Retention_Days × Row_Size

Exemplo: 172,800 × 90 dias × 2 KB = 31,104,000 KB ≈ 30 GB
```

### IOPS Necessário
```
IOPS = (Writes_per_Second + Reads_per_Second) × Safety_Factor

Exemplo: (20 + 10) × 1.5 = 45 IOPS
```

### Custo PostgreSQL RDS
```
Custo_DB = Instance_Price + (Storage_GB × Storage_Price) + (IOPS × IOPS_Price)

Exemplo: $50 + (50 GB × $0.115) + (100 IOPS × $0.10) = $65.75/mês
```

---

## ⚡ 6. CACHE (REDIS)

### Tamanho Cache
```
Cache_Size = (N_Cameras × Thumbnail_Size) + Session_Data + Query_Cache

Exemplo: (20 × 100 KB) + 10 MB + 50 MB = 62 MB
```

### Hit Rate
```
Hit_Rate = Cache_Hits / (Cache_Hits + Cache_Misses)

Exemplo: 900 / (900 + 100) = 0.9 = 90%
```

### Economia com Cache
```
Savings = Original_Cost × Hit_Rate

Exemplo: $1000 × 0.9 = $900 economizado
```

---

## 🔄 7. MENSAGERIA (RABBITMQ)

### Mensagens por Dia
```
Messages_Day = Detections_Day + Events_Day + Jobs_Day

Exemplo: 172,800 + 10,000 + 5,000 = 187,800 msgs/dia
```

### Throughput
```
Throughput = Messages_Day / 86400

Exemplo: 187,800 / 86400 = 2.17 msgs/s
```

### Tamanho Fila
```
Queue_Size = Throughput × Processing_Delay × Avg_Message_Size

Exemplo: 2.17 × 10s × 5 KB = 108.5 KB
```

---

## 💰 8. CUSTO TOTAL

### Custo Mensal por Cidade
```
Custo_Total = Banda + CPU + Storage + DB + Cache + Misc

Exemplo:
- Banda: $2,847
- CPU: $599
- Storage: $204
- DB: $66
- Cache: $15
- Misc: $100
Total: $3,831/mês
```

### Custo por Câmera
```
Custo_per_Camera = Custo_Total / N_Cameras

Exemplo: $3,831 / 20 = $191.55/câmera/mês
```

### ROI (Return on Investment)
```
ROI = (Revenue - Cost) / Cost × 100

Exemplo: ($10,000 - $3,831) / $3,831 × 100 = 161% ROI
```

---

## 📈 9. ESCALABILIDADE

### Câmeras Máximas (CPU)
```
Max_Cameras_CPU = Total_CPU_Cores / CPU_per_Camera

Exemplo: 32 cores / 1.5 = 21 câmeras
```

### Câmeras Máximas (Banda)
```
Max_Cameras_Bandwidth = Total_Bandwidth / Bandwidth_per_Camera

Exemplo: 1000 Mbps / 6 Mbps = 166 câmeras
```

### Câmeras Máximas (Storage)
```
Max_Cameras_Storage = Total_Storage / Storage_per_Camera

Exemplo: 10 TB / 443 GB = 22 câmeras
```

### Gargalo do Sistema
```
Max_Cameras = MIN(Max_CPU, Max_Bandwidth, Max_Storage)

Exemplo: MIN(21, 166, 22) = 21 câmeras (gargalo: CPU)
```

---

## 🎯 10. OTIMIZAÇÕES

### Economia Frame Skipping
```
Savings_CPU = Original_CPU × (1 - 1/Frame_Skip)

Exemplo: $599 × (1 - 1/3) = $599 × 0.667 = $399 economizado
```

### Economia Cache
```
Savings_Bandwidth = Original_Bandwidth × Cache_Hit_Rate

Exemplo: $5,000 × 0.9 = $4,500 economizado
```

### Economia Compressão
```
Savings_Storage = Original_Storage × (1 - Compression_Ratio)

Exemplo: $500 × (1 - 0.7) = $150 economizado
```

---

## 📊 11. MÉTRICAS DE PERFORMANCE

### Latência Média
```
Avg_Latency = Σ(Request_Time) / Total_Requests

Exemplo: 5000ms / 100 = 50ms
```

### P95 Latency
```
P95 = Latency no percentil 95

Exemplo: 95% das requisições < 200ms
```

### Throughput
```
Throughput = Successful_Requests / Time_Period

Exemplo: 10,000 req / 3600s = 2.78 req/s
```

### Error Rate
```
Error_Rate = Failed_Requests / Total_Requests × 100

Exemplo: 50 / 10,000 × 100 = 0.5%
```

### Uptime
```
Uptime = (Total_Time - Downtime) / Total_Time × 100

Exemplo: (720h - 1h) / 720h × 100 = 99.86%
```

---

## 🔢 12. CONSTANTES ÚTEIS

```python
# Tempo
SECONDS_PER_DAY = 86400
SECONDS_PER_HOUR = 3600
HOURS_PER_MONTH = 720
DAYS_PER_MONTH = 30

# Conversão
BITS_TO_BYTES = 8
KB_TO_MB = 1024
MB_TO_GB = 1024
GB_TO_TB = 1024

# AWS Pricing (us-east-1, 2026)
BANDWIDTH_PRICE = 0.09  # $/GB
S3_STORAGE_PRICE = 0.023  # $/GB/mês
EC2_T3_MEDIUM = 0.0416  # $/hora
RDS_DB_T3_SMALL = 0.034  # $/hora
ELASTICACHE_T3_MICRO = 0.017  # $/hora

# Compressão
H264_COMPRESSION = 0.1  # 10% do raw
H265_COMPRESSION = 0.05  # 5% do raw

# Detecção
YOLO_TIME_CPU = 0.1  # segundos/frame
OCR_TIME_CPU = 0.05  # segundos/placa
```

---

## 📝 Exemplo Completo: 20 Câmeras

```python
# Configuração
N_CAMERAS = 20
BITRATE = 6  # Mbps
FPS = 30
FRAME_SKIP = 3
RETENTION_DAYS = 7
VIEWERS = 5
CACHE_HIT_RATE = 0.9

# Streaming
bandwidth_total = N_CAMERAS * BITRATE * VIEWERS  # 600 Mbps
bandwidth_real = bandwidth_total * (1 - CACHE_HIT_RATE)  # 60 Mbps
bandwidth_cost = (bandwidth_real * 86400 * 30 / 8 / 1024) * 0.09  # $474/mês

# Detecção
fps_real = FPS / FRAME_SKIP  # 10 FPS
frames_day = N_CAMERAS * fps_real * 86400  # 17,280,000
cpu_hours = frames_day * 0.1 / 3600  # 480h
cpu_cost = (cpu_hours / 24) * 720 * 0.0416  # $599/mês

# Storage
size_per_camera = BITRATE * RETENTION_DAYS * 86400 / 8 / 1024  # 443 GB
storage_total = N_CAMERAS * size_per_camera  # 8,860 GB
storage_cost = storage_total * 0.023  # $204/mês

# Total
total_cost = bandwidth_cost + cpu_cost + storage_cost  # $1,277/mês
cost_per_camera = total_cost / N_CAMERAS  # $63.85/câmera/mês
```

---

**Versão:** 1.0  
**Data:** 2026-01-14  
**Autor:** VMS Team
