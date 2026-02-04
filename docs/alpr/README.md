# ALPR Service - Automatic License Plate Recognition

## Objetivo
Processar gravações de vídeo para detectar e reconhecer placas de veículos automaticamente.

## Arquitetura

```
┌─────────────────┐
│   Recordings    │
│  /recordings/   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ALPR Worker    │
│  - YOLOv8       │ ← Detecta veículos
│  - PaddleOCR    │ ← Lê placas
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│  - detections   │
│  - snapshots    │
└─────────────────┘
```

## Fluxo de Processamento

1. **Storage Service** indexa novo vídeo
2. **ALPR Worker** pega da fila (RabbitMQ)
3. **Processa vídeo**:
   - Extrai frames (1 a cada 10 frames)
   - YOLOv8 detecta veículos
   - Crop da região do veículo
   - PaddleOCR lê placa
   - Valida formato brasileiro (ABC-1234 ou ABC1D23)
4. **Salva resultado**:
   - Placa
   - Timestamp
   - Confiança (%)
   - Snapshot (JPEG)
   - Modelo/Cor (opcional)

## Tecnologias

- **YOLOv8**: Detecção de veículos
- **PaddleOCR**: OCR otimizado para placas BR
- **OpenCV**: Processamento de imagem
- **FastAPI**: API REST
- **PostgreSQL**: Armazenamento
- **RabbitMQ**: Fila de processamento

## Endpoints API

```
POST   /alpr/process/{camera_id}/{date}  - Processa vídeo específico
GET    /alpr/detections                  - Lista detecções
GET    /alpr/detections/{plate}          - Busca por placa
GET    /alpr/snapshot/{detection_id}     - Retorna snapshot
DELETE /alpr/detections/{id}             - Remove detecção
```

## Modelo de Dados

```sql
CREATE TABLE alpr_detections (
    id SERIAL PRIMARY KEY,
    camera_id INTEGER NOT NULL,
    plate VARCHAR(8) NOT NULL,
    confidence FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    snapshot_path VARCHAR(255),
    vehicle_type VARCHAR(50),
    vehicle_color VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_plate ON alpr_detections(plate);
CREATE INDEX idx_timestamp ON alpr_detections(timestamp);
```

## Configurações

```yaml
alpr:
  confidence_threshold: 0.7
  process_every_n_frames: 10
  max_concurrent_jobs: 2
  deduplication_window: 5  # segundos
```

## Próximos Passos

1. [ ] Implementar YOLOv8 para detecção
2. [ ] Integrar PaddleOCR
3. [ ] Criar worker com fila
4. [ ] Implementar API REST
5. [ ] Criar interface no frontend
6. [ ] Adicionar filtros e busca
7. [ ] Implementar alertas (placa específica)
