# Day 0 - Sistema de Gravação e Correções

## Data
2025-01-XX

## Resumo
Implementação do sistema de gravação otimizado, correção de bugs no RabbitMQ e Recorder, e melhorias na UI de câmeras.

---

## 1. Correção RabbitMQ - Erlang Cookie

### Problema
RabbitMQ falhava ao iniciar no Windows com erro de Erlang Cookie.

### Solução
Adicionado variável de ambiente `RABBITMQ_ERLANG_COOKIE` no docker-compose.yml:

```yaml
rabbitmq:
  environment:
    - RABBITMQ_ERLANG_COOKIE=GTVISIONERLANGCOOKIE2025
```

**Arquivo**: `docker-compose.yml`

---

## 2. Sistema de Snapshot Estático

### Objetivo
Reduzir consumo de banda de ~2KB/seg por câmera para carga única de ~20-50KB.

### Implementação

#### Backend (Streaming Service)
- Endpoint: `GET /streaming/cameras/{id}/snapshot`
- Captura 1 frame via FFmpeg do stream RTSP
- Cache no Redis por 24h
- Retorna JPEG otimizado

#### Frontend (StreamThumbnail.tsx)
- Fetch único do snapshot na montagem do componente
- Armazenamento em `localStorage` com chave `camera_snapshot_{id}`
- Indicador de status baseado em `camera.status` (não na disponibilidade do snapshot)
- Remoção de polling contínuo

**Arquivos**:
- `services/streaming/main.py` (endpoint `/cameras/{id}/snapshot`)
- `frontend/src/components/cameras/StreamThumbnail.tsx`

---

## 3. Sistema de Gravação Contínua

### Decisão Arquitetural
**Gravação contínua 24/7** ao invés de detecção de movimento para:
- Simplicidade operacional
- Confiabilidade (sem perda de eventos)
- Reprocessamento offline de ALPR e Analytics

### Configuração MediaMTX
```yaml
sourceOnDemand: no          # Conexão RTSP sempre ativa
record: no                  # Gravação delegada ao Recorder Service
recordDeleteAfter: 168h     # Retenção de 7 dias
```

**Arquivo**: `mediamtx.yml`

### Cálculo de Storage

#### Stream Original (5Mbps)
- 34.4 MB/min
- 2.064 GB/hora
- 49.5 GB/dia/câmera
- 346 GB/7dias/câmera
- **4.15 TB para 12 câmeras**

#### Stream Otimizado (2Mbps - Recorder Service)
- 13.8 MB/min
- 828 MB/hora
- 19.9 GB/dia/câmera
- 139 GB/7dias/câmera
- **1.7 TB para 12 câmeras**

---

## 4. Recorder Service

### Objetivo
Re-encodar streams em bitrate reduzido para otimizar armazenamento.

### Características
- Bitrate: 2Mbps (vs 5Mbps do stream original)
- CRF: 28 (qualidade média-baixa, suficiente para ALPR)
- Segmentação: 1 arquivo por dia (86400 segundos)
- Preset: veryfast (baixo uso de CPU)
- Áudio: AAC 64kbps

### Estrutura de Arquivos
```
/recordings/
  cam_1/
    2025-01-15/
      00-00-00.mp4  (24h de gravação)
    2025-01-16/
      00-00-00.mp4
  cam_2/
    ...
```

### FFmpeg Command
```bash
ffmpeg -y \
  -rtsp_transport tcp \
  -i rtsp://mediamtx:8554/cam_{id} \
  -c:v libx264 \
  -preset veryfast \
  -crf 28 \
  -maxrate 2M \
  -bufsize 4M \
  -c:a aac \
  -b:a 64k \
  -f segment \
  -segment_time 86400 \
  -segment_format mp4 \
  -reset_timestamps 1 \
  -strftime 1 \
  /recordings/cam_{id}/%Y-%m-%d/%H-%M-%S.mp4
```

### Docker Service
```yaml
recorder:
  build: ./services/recorder
  volumes:
    - recordings:/recordings
  depends_on:
    - backend
    - mediamtx
  restart: unless-stopped
```

**Arquivos**:
- `services/recorder/recorder.py`
- `services/recorder/Dockerfile`
- `services/recorder/requirements.txt`
- `docker-compose.yml`

---

## 5. Clips Service

### Objetivo
Permitir extração de segmentos de 5 minutos das gravações com opções de qualidade.

### API Endpoints

#### POST /clips/create
```json
{
  "camera_id": 1,
  "start_time": "2025-01-15T14:30:00",
  "duration": 300,
  "quality": "medium"
}
```

#### GET /clips/{id}
Retorna metadados do clip.

#### GET /clips/{id}/download
Download do arquivo MP4.

#### DELETE /clips/{id}
Remove clip do storage.

### Qualidades Disponíveis
- **low**: CRF 28, 1Mbps
- **medium**: CRF 23, 2Mbps
- **high**: CRF 18, 5Mbps (qualidade original)

### Integração Django
- App `clips` no backend Django
- Modelo com campos: `external_id`, `status`, `camera`, `start_time`, `duration`, `quality`
- Comunicação via httpx com Clips Service

**Arquivos**:
- `services/clips/main.py`
- `services/clips/Dockerfile`
- `backend/apps/clips/models.py`
- `backend/apps/clips/views.py`
- `backend/apps/clips/serializers.py`

---

## 6. UI - Câmeras (Apenas Lista + Paginação)

### Mudanças
- ❌ Removido: Grid view e toggle de visualização
- ✅ Mantido: List view apenas
- ✅ Adicionado: Paginação (10 itens por página)

### Componentes de Paginação
- Botões Previous/Next com ícones ChevronLeft/ChevronRight
- Contador: "Showing X to Y of Z cameras"
- Desabilitação automática em primeira/última página

**Arquivo**: `frontend/src/pages/CamerasPage.tsx`

---

## 7. Correção Recorder Service - Autenticação

### Problema
```
AttributeError: 'str' object has no attribute 'get'
HTTP 401 Unauthorized
```

### Causa
1. Backend retorna 401 (não autenticado)
2. Response é string de erro, não lista de câmeras
3. Código tentava fazer `cam.get("enabled")` em string

### Solução
```python
async def main():
    client = httpx.AsyncClient()
    
    try:
        resp = await client.get("http://backend:8000/api/cameras/")
        
        if resp.status_code == 401:
            logger.error("❌ Não autorizado - Backend requer autenticação")
            return
        
        resp.raise_for_status()
        cameras = resp.json()
        
        if not isinstance(cameras, list):
            logger.error(f"❌ Resposta inválida do backend: {cameras}")
            return
        
        # ... resto do código
```

**Arquivo**: `services/recorder/recorder.py`

### Próximos Passos
- [ ] Implementar autenticação service-to-service (JWT ou API Key)
- [ ] Ou tornar endpoint `/api/cameras/` público para serviços internos

---

## 8. Documentação Futura

### Criados em docs/
- `docs/alpr/README.md` - Sistema de reconhecimento de placas
- `docs/analytics/README.md` - Análise de vídeo (contagem, detecção)
- `docs/clips/README.md` - Serviço de extração de clips

---

## Arquitetura Final

```
┌─────────────┐
│   Frontend  │ (React + TypeScript)
└──────┬──────┘
       │
┌──────▼──────┐
│   Backend   │ (Django REST)
│  (port 8000)│
└──────┬──────┘
       │
       ├─────────────┐
       │             │
┌──────▼──────┐ ┌───▼────────┐
│  Streaming  │ │   Clips    │
│ (port 8001) │ │(port 8004) │
└──────┬──────┘ └────────────┘
       │
┌──────▼──────┐
│  MediaMTX   │ (RTSP/HLS)
│ RTSP: 8554  │
│ HLS:  8888  │
└──────┬──────┘
       │
       ├─────────────┐
       │             │
┌──────▼──────┐ ┌───▼────────┐
│  Recorder   │ │    LPR     │
│ (optimized) │ │  (offline) │
└─────────────┘ └────────────┘
```

---

## Volumes Docker

```yaml
volumes:
  postgres_data:      # Banco de dados
  redis_data:         # Cache
  recordings:         # Gravações otimizadas (1.7TB)
  clips_storage:      # Clips extraídos
```

---

## Métricas de Performance

### Banda por Câmera
- **Antes (polling)**: ~2 KB/s contínuo
- **Depois (snapshot)**: ~20-50 KB carga única

### Storage (12 câmeras, 7 dias)
- **Stream original**: 4.15 TB
- **Recorder otimizado**: 1.7 TB
- **Economia**: 59% de redução

### Retenção
- Gravações: 7 dias (168h)
- Snapshots (Redis): 24h
- Clips: Indefinido (gerenciado pelo usuário)

---

## Comandos Úteis

### Rebuild Recorder
```bash
docker-compose up -d --build recorder
```

### Ver logs do Recorder
```bash
docker-compose logs -f recorder
```

### Limpar gravações antigas
```bash
docker exec -it vms-recorder-1 find /recordings -type f -mtime +7 -delete
```

### Verificar espaço usado
```bash
docker exec -it vms-recorder-1 du -sh /recordings/*
```

---

## Issues Conhecidos

1. **Recorder 401 Unauthorized**: Backend requer autenticação para `/api/cameras/`
   - Solução temporária: Tratamento de erro implementado
   - Solução definitiva: Implementar auth service-to-service

2. **Snapshot inicial vazio**: Primeira requisição pode falhar se stream não estiver pronto
   - Solução: Frontend usa placeholder até snapshot estar disponível

---

## Próximas Implementações

1. **ALPR Offline** (docs/alpr/)
   - Processar gravações para detectar placas
   - YOLOv8 + PaddleOCR
   - Armazenar em banco com timestamp

2. **Analytics** (docs/analytics/)
   - Contagem de pessoas/veículos
   - Detecção de eventos (invasão, abandono)
   - Heatmaps

3. **Autenticação Service-to-Service**
   - JWT ou API Keys
   - Middleware no Django

4. **Dashboard de Storage**
   - Monitorar espaço usado
   - Alertas de capacidade
   - Limpeza automática
