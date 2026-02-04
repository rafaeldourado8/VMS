# Clips Service - Video Clipping

## Objetivo
Recortar trechos específicos de vídeos gravados para download, compartilhamento ou análise.

## Arquitetura

```
┌──────────────┐
│   Frontend   │
│  Seleciona   │
│  trecho      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Clips     │
│   Service    │
│  (FastAPI)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   FFmpeg     │
│   Worker     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    /clips/   │
│   Storage    │
└──────────────┘
```

## Funcionalidades

### 1. **Recorte Simples**
- Início e fim
- Formato original
- Download direto

### 2. **Recorte com Processamento**
- Redimensionar
- Adicionar marca d'água
- Converter formato
- Ajustar qualidade

### 3. **Recorte de Evento**
- Baseado em detecção ALPR
- Baseado em analytics
- Buffer antes/depois

### 4. **Compartilhamento**
- Link temporário
- Expiração configurável
- Proteção por senha (opcional)

## Fluxo de Processamento

1. **Usuário solicita clip**:
   - Câmera
   - Data/Hora início
   - Data/Hora fim (máx 5 min)
   - Opções (formato, qualidade)

2. **Sistema valida**:
   - Vídeo existe?
   - Período válido?
   - Espaço disponível?

3. **Worker processa**:
   - FFmpeg extrai trecho
   - Aplica processamento
   - Salva em /clips/

4. **Retorna**:
   - URL de download
   - Expiração
   - Tamanho do arquivo

## Endpoints API

```
POST   /clips/create              - Cria novo clip
GET    /clips                     - Lista clips
GET    /clips/{id}                - Info do clip
GET    /clips/{id}/download       - Download
DELETE /clips/{id}                - Remove clip
POST   /clips/{id}/share          - Gera link compartilhável
GET    /clips/shared/{token}      - Acessa clip compartilhado
```

## Modelo de Dados

```sql
CREATE TABLE clips (
    id SERIAL PRIMARY KEY,
    camera_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    duration INTEGER NOT NULL,
    file_path VARCHAR(255),
    file_size BIGINT,
    format VARCHAR(10),
    status VARCHAR(20),
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE TABLE clip_shares (
    id SERIAL PRIMARY KEY,
    clip_id INTEGER REFERENCES clips(id),
    token VARCHAR(64) UNIQUE,
    password_hash VARCHAR(255),
    expires_at TIMESTAMP,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Exemplo de Requisição

```json
{
  "camera_id": 1,
  "start_time": "2024-02-04T10:30:00",
  "end_time": "2024-02-04T10:32:00",
  "options": {
    "format": "mp4",
    "quality": "medium",
    "watermark": true,
    "resize": "1280x720"
  }
}
```

## Exemplo de Resposta

```json
{
  "id": 456,
  "status": "completed",
  "download_url": "/clips/456/download",
  "file_size": 15728640,
  "duration": 120,
  "expires_at": "2024-02-11T10:30:00",
  "share_url": null
}
```

## Processamento FFmpeg

### Recorte Simples (Copy)
```bash
ffmpeg -ss 00:00:10 -i input.mp4 -t 00:02:00 -c copy output.mp4
```

### Recorte com Recodificação
```bash
ffmpeg -ss 00:00:10 -i input.mp4 -t 00:02:00 \
  -vf "scale=1280:720,drawtext=text='Camera 1':x=10:y=10" \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 128k \
  output.mp4
```

### Recorte Otimizado (Seek Rápido)
```bash
ffmpeg -ss 00:00:10 -i input.mp4 -t 00:02:00 \
  -c:v libx264 -preset ultrafast -crf 23 \
  -movflags +faststart \
  output.mp4
```

## Configurações

```yaml
clips:
  max_duration_minutes: 5
  max_concurrent_jobs: 3
  storage_path: /clips
  retention_days: 7
  formats:
    - mp4
    - webm
    - avi
  quality_presets:
    low: {crf: 28, bitrate: "1M"}
    medium: {crf: 23, bitrate: "2M"}
    high: {crf: 18, bitrate: "4M"}
```

## Limpeza Automática

```python
# Cron job diário
DELETE FROM clips WHERE expires_at < NOW();
# Remove arquivos físicos
```

## Próximos Passos

1. [ ] Implementar API de clips
2. [ ] Criar worker FFmpeg
3. [ ] Sistema de fila (RabbitMQ)
4. [ ] Interface no frontend
5. [ ] Sistema de compartilhamento
6. [ ] Limpeza automática
7. [ ] Integração com ALPR/Analytics
8. [ ] Preview de clip antes de criar
