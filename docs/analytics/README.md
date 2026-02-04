# Analytics Service - Video Analysis

## Objetivo
Análise profunda de vídeos sob demanda para extrair insights e detectar eventos.

## Arquitetura

```
┌──────────────┐
│   Frontend   │
│  Seleciona   │
│  período     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Analytics   │
│   Service    │
│  (FastAPI)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  RabbitMQ    │
│    Queue     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Analytics   │
│   Worker     │
│  - YOLOv8    │
│  - DeepSORT  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │
│  + Results   │
└──────────────┘
```

## Tipos de Análise

### 1. **Contagem de Pessoas**
- Entrada/Saída
- Permanência
- Heatmap de movimento

### 2. **Análise de Veículos**
- Contagem por tipo
- Velocidade média
- Tempo de permanência

### 3. **Detecção de Eventos**
- Aglomeração
- Objeto abandonado
- Invasão de área
- Comportamento suspeito

### 4. **Análise de Fluxo**
- Direção predominante
- Horários de pico
- Padrões de movimento

## Fluxo de Processamento

1. **Usuário seleciona**:
   - Câmera
   - Data/Hora início
   - Data/Hora fim (máx 10 min)
   - Tipo de análise

2. **Sistema cria job**:
   - Status: pending
   - Progress: 0%

3. **Worker processa**:
   - Carrega vídeo
   - Aplica modelos
   - Atualiza progresso
   - Gera relatório

4. **Resultado disponível**:
   - JSON com dados
   - Gráficos
   - Vídeo anotado (opcional)

## Endpoints API

```
POST   /analytics/jobs                - Cria job de análise
GET    /analytics/jobs                - Lista jobs
GET    /analytics/jobs/{id}           - Status do job
GET    /analytics/jobs/{id}/result    - Resultado
DELETE /analytics/jobs/{id}           - Cancela/Remove job
GET    /analytics/jobs/{id}/video     - Vídeo anotado
```

## Modelo de Dados

```sql
CREATE TABLE analytics_jobs (
    id SERIAL PRIMARY KEY,
    camera_id INTEGER NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,
    progress INTEGER DEFAULT 0,
    result JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TABLE analytics_results (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES analytics_jobs(id),
    metric_name VARCHAR(100),
    metric_value JSONB,
    timestamp TIMESTAMP
);
```

## Exemplo de Resultado

```json
{
  "job_id": 123,
  "analysis_type": "people_counting",
  "period": {
    "start": "2024-02-04T10:00:00",
    "end": "2024-02-04T10:10:00"
  },
  "results": {
    "total_people": 45,
    "avg_people": 12,
    "peak_time": "10:05:30",
    "peak_count": 18,
    "entries": 23,
    "exits": 21,
    "timeline": [
      {"time": "10:00:00", "count": 10},
      {"time": "10:01:00", "count": 12}
    ]
  },
  "heatmap_url": "/analytics/jobs/123/heatmap.png"
}
```

## Modelos Utilizados

- **YOLOv8**: Detecção de objetos
- **DeepSORT**: Tracking de objetos
- **ByteTrack**: Tracking alternativo
- **OpenPose**: Pose estimation (opcional)

## Configurações

```yaml
analytics:
  max_duration_minutes: 10
  max_concurrent_jobs: 1
  models:
    yolov8: yolov8n.pt
    deepsort: deep_sort.pth
  output:
    save_annotated_video: false
    save_heatmap: true
```

## Próximos Passos

1. [ ] Implementar API de jobs
2. [ ] Criar worker com YOLOv8
3. [ ] Adicionar tracking (DeepSORT)
4. [ ] Implementar contagem de pessoas
5. [ ] Criar visualizações (gráficos)
6. [ ] Interface no frontend
7. [ ] Adicionar mais tipos de análise
