# 📡 Arquitetura de Streaming e Failover - VMS

**Versão:** 1.0  
**Data:** Janeiro 2026  
**Status:** PRÉ-IMPLEMENTAÇÃO (Crítico antes da IA)

---

## 🎯 Objetivo

Garantir **alta disponibilidade** de streaming e gravação 24/7 com recuperação automática de falhas, adequado para ambientes de prefeituras e órgãos públicos.

---

## 🏗️ Arquitetura Geral

```
┌─────────┐
│ Câmera  │
│ (RTSP)  │
└────┬────┘
     │
     ↓
┌────────────────────────────────────┐
│         MediaMTX Server            │
│  ┌──────────────────────────────┐  │
│  │  Stream Processing           │  │
│  │  • WebRTC (live primário)    │  │
│  │  • HLS (fallback + gravação) │  │
│  └──────────────────────────────┘  │
└────┬───────────────────────────┬───┘
     │                           │
     ↓                           ↓
┌─────────┐              ┌──────────────┐
│ WebRTC  │              │ HLS Recording│
│ (Live)  │              │   (24/7)     │
└────┬────┘              └──────┬───────┘
     │                          │
     ↓                          ↓
┌─────────────┐          ┌─────────────┐
│  Frontend   │          │ S3 Glacier  │
│  (Viewer)   │          │  (Backup)   │
└─────────────┘          └─────────────┘
     ↑
     │ (fallback automático)
     │
┌────┴────┐
│   HLS   │
│ (Live)  │
└─────────┘
```

---

## 📺 Estratégia de Streaming

### **Modo Live (Monitoramento em Tempo Real)**

**Protocolo Primário: WebRTC**
- Latência: < 500ms
- Tentativas: 3x com timeout de 5s cada
- Total de espera: 15s máximo

**Protocolo Fallback: HLS**
- Latência: 4-6s
- Ativação: Automática após falha do WebRTC
- Compatibilidade: 100% dos navegadores

**Fluxo de Decisão:**
```
1. Tenta WebRTC (3x)
   ├─ Sucesso → Exibe 🟢 "Latência mínima"
   └─ Falha → Muda para HLS
2. Carrega HLS
   └─ Exibe 🟡 "Modo estável"
```

### **Modo Playback (Gravações)**

**Protocolo Único: HLS**
- Usa os mesmos arquivos da gravação contínua
- Sem necessidade de transcodificação
- Seek/scrubbing nativo

---

## 💾 Sistema de Gravação

### **Gravação Contínua Obrigatória**

**Características:**
- Formato: fMP4 (melhor para playback)
- Segmentos: 60 segundos por arquivo
- Retenção: 90 dias (configurável)
- Path: `/recordings/YYYY-MM-DD/HH-MM-SS-cam_{id}/`

**Independência Crítica:**
- Gravação **NUNCA** depende de visualização
- HLS grava mesmo sem usuários conectados
- Prioridade máxima do sistema

### **Configuração MediaMTX**

```yaml
paths:
  cam_{id}:
    source: rtsp://camera_url
    sourceOnDemand: false  # Sempre ativo
    
    # Gravação (CRÍTICO)
    record: yes
    recordPath: /recordings/%Y-%m-%d/%H-%M-%S-cam_{id}
    recordFormat: fmp4
    recordSegmentDuration: 60s
    recordDeleteAfter: 2160h  # 90 dias
    
    # WebRTC (Live primário)
    webrtc: yes
    webrtcICEServers:
      - urls: ["stun:stun.l.google.com:19302"]
    
    # HLS (Fallback + base da gravação)
    hls: yes
    hlsSegmentDuration: 2s
    hlsSegmentCount: 5
    hlsAllowOrigin: '*'
```

---

## 🔄 Sistema de Failover Automático

### **Monitoramento Contínuo**

**Frequência:** A cada 30 segundos  
**Executor:** Celery Beat Task

**Verificações:**

1. **Stream Ativo**
   - Endpoint: `GET /v3/paths/get/cam_{id}`
   - Timeout: 3s
   - Critério: `status == 200 && ready == true`

2. **Gravação Ativa** (CRÍTICO)
   - Verifica arquivo mais recente
   - Critério: Modificado há menos de 2 minutos
   - Falha = Alerta crítico imediato

3. **HLS Disponível**
   - Endpoint: `GET /cam_{id}/index.m3u8`
   - Timeout: 3s
   - Critério: `status == 200`

### **Ações de Recuperação**

#### **Nível 1: Recuperação de Stream**
```python
Trigger: Stream inativo
Ação:
  1. Remove path do MediaMTX
  2. Aguarda 2s
  3. Recria path com configuração original
  4. Aguarda 10s
  5. Verifica se recuperou
Alerta: Info (log apenas)
```

#### **Nível 2: Recuperação de Gravação**
```python
Trigger: Gravação parada (> 2min sem arquivo novo)
Ação:
  1. Executa recuperação de stream
  2. Aguarda 10s
  3. Verifica gravação novamente
  4. Se falhar → Alerta CRÍTICO
Alerta: CRÍTICO (Telegram + Dashboard)
```

#### **Nível 3: Falha Persistente**
```python
Trigger: 3 falhas consecutivas
Ação:
  1. Marca câmera como offline
  2. Para tentativas de recuperação
  3. Alerta CRÍTICO com detalhes
  4. Requer intervenção manual
Alerta: CRÍTICO (Telegram + Email + Dashboard)
```

---

## 🚨 Sistema de Alertas

### **Níveis de Severidade**

| Nível | Quando | Ação |
|-------|--------|------|
| **Info** | Stream reconectou com sucesso | Log apenas |
| **Warning** | 1ª falha de stream | Log + Dashboard |
| **Critical** | Gravação parou OU 3 falhas consecutivas | Log + Dashboard + Telegram + Email |

### **Canais de Notificação**

**1. Dashboard (Tempo Real)**
```
🟢 Online: 12 câmeras
🟡 Recuperando: 1 câmera
🔴 Offline: 0 câmeras

Alertas Recentes:
• 14:32 - Câmera Portaria: Gravação recuperada
• 14:15 - Câmera Estacionamento: Stream reconectado
```

**2. Telegram (Crítico)**
```
🚨 ALERTA CRÍTICO
Câmera: Portaria Principal
Problema: Gravação não recuperada após 3 tentativas
Horário: 14:35:22
Ação: Verificar câmera fisicamente
```

**3. Logs Estruturados**
```json
{
  "timestamp": "2026-01-05T14:35:22Z",
  "level": "CRITICAL",
  "camera_id": 5,
  "camera_name": "Portaria Principal",
  "issue": "recording_stopped",
  "recovery_attempts": 3,
  "last_recording": "2026-01-05T14:20:15Z"
}
```

---

## 📊 Métricas de Saúde

### **Indicadores Principais**

1. **Uptime de Gravação**: > 99.9%
2. **Tempo de Recuperação**: < 60s
3. **Taxa de Falhas**: < 1% por dia
4. **Latência Live (WebRTC)**: < 500ms
5. **Latência Fallback (HLS)**: < 6s

### **Dashboard de Monitoramento**

**Endpoint:** `GET /api/cameras/health`

**Resposta:**
```json
{
  "total": 15,
  "online": 14,
  "recovering": 1,
  "offline": 0,
  "recording_health": {
    "active": 15,
    "failed": 0,
    "disk_usage": "45%"
  },
  "recent_alerts": [
    {
      "camera": "Portaria",
      "severity": "warning",
      "message": "Stream reconectado",
      "timestamp": "2026-01-05T14:32:00Z",
      "resolved": true
    }
  ]
}
```

---

## 📈 Observabilidade: Prometheus + Grafana

### **Arquitetura de Monitoramento**

```
┌──────────────┐
│   Django     │ ──→ django-prometheus ──→ /metrics
└──────────────┘

┌──────────────┐
│  MediaMTX    │ ──→ metrics endpoint ──→ :9998/metrics
└──────────────┘

┌──────────────┐
│   Celery     │ ──→ celery-exporter ──→ /metrics
└──────────────┘

┌──────────────┐
│ Node Exporter│ ──→ system metrics ──→ :9100/metrics
└──────────────┘
         ↓
         ↓ (scrape a cada 15s)
         ↓
┌──────────────┐
│  Prometheus  │ ──→ armazena séries temporais
└──────┬───────┘
       │
       ↓ (query)
┌──────────────┐
│   Grafana    │ ──→ dashboards + alertas
└──────────────┘
```

### **Métricas Coletadas**

#### **1. Métricas de Câmeras (Custom)**
```python
# apps/cameras/metrics.py
from prometheus_client import Counter, Gauge, Histogram

# Status das câmeras
camera_status = Gauge(
    'vms_camera_status',
    'Status da câmera (1=online, 0=offline)',
    ['camera_id', 'camera_name']
)

# Gravação ativa
recording_active = Gauge(
    'vms_recording_active',
    'Gravação ativa (1=sim, 0=não)',
    ['camera_id']
)

# Falhas de recuperação
recovery_failures = Counter(
    'vms_recovery_failures_total',
    'Total de falhas de recuperação',
    ['camera_id', 'failure_type']
)

# Latência de stream
stream_latency = Histogram(
    'vms_stream_latency_seconds',
    'Latência do stream em segundos',
    ['camera_id', 'protocol']
)

# Uso de disco
disk_usage = Gauge(
    'vms_disk_usage_percent',
    'Uso de disco em porcentagem',
    ['mount_point']
)

# Alertas ativos
active_alerts = Gauge(
    'vms_active_alerts',
    'Número de alertas ativos',
    ['severity']
)
```

#### **2. Métricas do MediaMTX (Nativas)**
- `mediamtx_paths_total` - Total de paths configurados
- `mediamtx_paths_bytes_received` - Bytes recebidos por path
- `mediamtx_paths_bytes_sent` - Bytes enviados por path
- `mediamtx_rtsp_sessions` - Sessões RTSP ativas
- `mediamtx_hls_sessions` - Sessões HLS ativas
- `mediamtx_webrtc_sessions` - Sessões WebRTC ativas

#### **3. Métricas do Sistema (Node Exporter)**
- CPU, memória, disco
- I/O de disco
- Rede (bytes in/out)
- Temperatura (se disponível)

#### **4. Métricas do Django (django-prometheus)**
- Requisições HTTP (latência, status)
- Queries do banco de dados
- Tamanho de cache
- Exceções

### **Configuração Prometheus**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Django/Backend
  - job_name: 'vms-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
  
  # MediaMTX
  - job_name: 'mediamtx'
    static_configs:
      - targets: ['mediamtx:9998']
  
  # Node Exporter (sistema)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
  
  # Celery
  - job_name: 'celery'
    static_configs:
      - targets: ['celery-exporter:9808']

# Regras de alerta
rule_files:
  - '/etc/prometheus/alerts.yml'

# Alertmanager
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
```

### **Regras de Alerta Prometheus**

```yaml
# alerts.yml
groups:
  - name: vms_critical
    interval: 30s
    rules:
      # Câmera offline
      - alert: CameraOffline
        expr: vms_camera_status == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Câmera {{ $labels.camera_name }} offline"
          description: "Câmera ID {{ $labels.camera_id }} está offline há mais de 1 minuto"
      
      # Gravação parada
      - alert: RecordingStopped
        expr: vms_recording_active == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Gravação parou na câmera {{ $labels.camera_id }}"
          description: "CRÍTICO: Gravação não está ativa há mais de 2 minutos"
      
      # Disco cheio
      - alert: DiskAlmostFull
        expr: vms_disk_usage_percent > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Disco quase cheio: {{ $value }}%"
          description: "Uso de disco em {{ $labels.mount_point }} está acima de 85%"
      
      # Muitas falhas de recuperação
      - alert: HighRecoveryFailureRate
        expr: rate(vms_recovery_failures_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Taxa alta de falhas de recuperação"
          description: "Câmera {{ $labels.camera_id }} com muitas falhas de recuperação"
      
      # MediaMTX sem sessões
      - alert: NoActiveSessions
        expr: sum(mediamtx_hls_sessions + mediamtx_webrtc_sessions) == 0
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Nenhuma sessão ativa no MediaMTX"
          description: "Pode indicar problema no servidor de streaming"
```

### **Dashboards Grafana**

#### **Dashboard 1: Visão Geral do Sistema**

**Painéis:**
- Status de todas as câmeras (mapa de calor)
- Total online/offline/recuperando
- Uso de disco em tempo real
- Alertas ativos (últimas 24h)
- Taxa de falhas por hora

**Queries PromQL:**
```promql
# Total de câmeras online
sum(vms_camera_status)

# Taxa de uptime (últimas 24h)
avg_over_time(vms_camera_status[24h]) * 100

# Uso de disco
vms_disk_usage_percent{mount_point="/recordings"}

# Alertas críticos ativos
vms_active_alerts{severity="critical"}
```

#### **Dashboard 2: Performance de Streaming**

**Painéis:**
- Latência por protocolo (WebRTC vs HLS)
- Sessões ativas por tipo
- Bandwidth por câmera
- Frames perdidos
- Tempo de recuperação médio

**Queries PromQL:**
```promql
# Latência média por protocolo
avg(vms_stream_latency_seconds) by (protocol)

# Sessões WebRTC ativas
mediamtx_webrtc_sessions

# Bytes enviados por câmera
rate(mediamtx_paths_bytes_sent[5m])

# Tempo médio de recuperação
avg(vms_recovery_duration_seconds)
```

#### **Dashboard 3: Gravações**

**Painéis:**
- Status de gravação por câmera
- Espaço usado por câmera
- Taxa de gravação (MB/s)
- Previsão de espaço disponível
- Histórico de falhas de gravação

**Queries PromQL:**
```promql
# Gravações ativas
sum(vms_recording_active)

# Taxa de crescimento de disco
rate(vms_disk_usage_bytes[1h])

# Previsão de dias até disco cheio
predict_linear(vms_disk_usage_bytes[24h], 7*24*3600)
```

### **Configuração Docker Compose**

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/alerts.yml:/etc/prometheus/alerts.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'
  
  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
  
  node-exporter:
    image: prom/node-exporter:latest
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
  
  alertmanager:
    image: prom/alertmanager:latest
    volumes:
      - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml
    ports:
      - "9093:9093"

volumes:
  prometheus-data:
  grafana-data:
```

### **Integração com Django**

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'django_prometheus',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... outros middlewares
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path('metrics/', include('django_prometheus.urls')),
]
```

### **Atualização de Métricas no Failover**

```python
# apps/cameras/failover.py
from .metrics import (
    camera_status, recording_active, 
    recovery_failures, stream_latency
)

def check_camera_health(camera):
    health = # ... verificação
    
    # Atualiza métricas Prometheus
    camera_status.labels(
        camera_id=camera.id,
        camera_name=camera.name
    ).set(1 if health['ok'] else 0)
    
    recording_active.labels(
        camera_id=camera.id
    ).set(1 if health['recording'] else 0)
    
    return health

def recover_stream(camera):
    try:
        # ... lógica de recuperação
        return True
    except Exception as e:
        recovery_failures.labels(
            camera_id=camera.id,
            failure_type='stream'
        ).inc()
        return False
```

### **Alertmanager para Telegram**

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'camera_id']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'telegram'

receivers:
  - name: 'telegram'
    webhook_configs:
      - url: 'http://backend:8000/api/alerts/webhook'
        send_resolved: true
```

---

## 🔧 Implementação Técnica

### **Componentes Necessários**

**Backend:**
- `apps/cameras/failover.py` - Sistema de monitoramento e recuperação
- `apps/cameras/models.py` - Model CameraAlert
- `apps/cameras/tasks.py` - Tarefas Celery
- `apps/cameras/api.py` - Endpoints de saúde

**Configuração:**
- Celery Beat (scheduler)
- Redis (broker)
- MediaMTX configurado

**Frontend:**
- Componente de status em tempo real
- Banner de alertas críticos
- Indicador de protocolo ativo

### **Dependências**

```txt
celery==5.3.4
redis==5.0.1
requests==2.31.0
boto3==1.34.0  # Para backup S3
django-prometheus==2.3.1
prometheus-client==0.19.0
```

### **Variáveis de Ambiente**

```env
# MediaMTX
MEDIAMTX_API=http://mediamtx:9997
MEDIAMTX_HLS_URL=http://mediamtx:8888
MEDIAMTX_WEBRTC_URL=http://mediamtx:8889

# Gravação
RECORDINGS_PATH=/recordings
RECORDINGS_RETENTION_DAYS=90

# Alertas
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
ALERT_EMAIL=admin@prefeitura.gov.br

# S3 Backup
AWS_S3_BUCKET=vms-recordings
AWS_STORAGE_CLASS=GLACIER_IR

# Prometheus/Grafana
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
```

---

## ✅ Checklist de Validação

Antes de implementar IA, garantir que:

- [ ] MediaMTX configurado com gravação contínua
- [ ] Celery Beat rodando e executando monitor a cada 30s
- [ ] Recuperação automática de stream funcionando
- [ ] Recuperação automática de gravação funcionando
- [ ] Alertas críticos chegando no Telegram
- [ ] Dashboard mostrando status em tempo real
- [ ] WebRTC funcionando como primário
- [ ] Fallback HLS ativando automaticamente
- [ ] Playback de gravações funcionando
- [ ] Backup S3 configurado (opcional para MVP)
- [ ] Logs estruturados sendo gerados
- [ ] Teste de falha simulada (desconectar câmera)
- [ ] Teste de recuperação (reconectar câmera)
- [ ] Teste de 3 falhas consecutivas
- [ ] Teste de disco cheio (> 90%)
- [ ] Prometheus coletando métricas de todos os componentes
- [ ] Grafana com dashboards configurados
- [ ] Alertas Prometheus funcionando
- [ ] Integração Alertmanager → Telegram

---

## 🎯 Critérios de Sucesso

**Sistema está pronto quando:**

1. ✅ Câmera desconectada é detectada em < 30s
2. ✅ Stream é recuperado automaticamente em < 60s
3. ✅ Gravação NUNCA para (mesmo com falha de stream)
4. ✅ Alerta crítico chega em < 5s após falha de gravação
5. ✅ Dashboard reflete status real em < 10s
6. ✅ WebRTC funciona com latência < 500ms
7. ✅ Fallback HLS ativa em < 2s após falha WebRTC
8. ✅ Sistema opera 24h sem intervenção manual

---

## 📝 Próximos Passos

**Após validação completa:**

1. Documentar testes realizados
2. Treinar equipe de operação
3. Configurar alertas para equipe técnica
4. Implementar backup S3 (se não feito)
5. **Iniciar implementação da IA** (apenas após tudo acima validado)

---

## ⚠️ Avisos Importantes

1. **NUNCA** implemente IA antes de validar streaming/gravação
2. **Gravação é prioridade máxima** - IA pode ser pausada, gravação não
3. **Teste em produção** com 1-2 câmeras antes de escalar
4. **Monitore disco** - gravação 24/7 consome ~50GB/câmera/mês
5. **Backup é obrigatório** para prefeituras (requisito legal)

---

**Documento aprovado para implementação:** ⬜  
**Data de aprovação:** ___/___/______  
**Responsável técnico:** _________________
