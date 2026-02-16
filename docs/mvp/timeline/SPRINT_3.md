# Sprint 3: Indexação e Timeline

## Objetivo
Implementar a lógica de indexação de gravações e geração de timeline

## Checklist

### 📁 FastAPI - Indexação
- [x] `indexer.py` - Módulo de indexação
  - [x] scan_recordings_directory()
  - [x] index_camera_recordings()
  - [x] get_video_metadata() usando ffprobe
  - [x] build_timeline_blocks()
- [x] `cache.py` - Cache em memória
  - [x] Cache de índices por câmera
  - [x] TTL configurável
  - [x] Invalidação automática
- [x] `filesystem.py` - Utilitários de filesystem
  - [x] list_recording_files()
  - [x] get_file_stats()
  - [x] parse_filename_timestamp()

### 🎯 Endpoints Timeline
- [x] `GET /timeline/{camera_id}` - Timeline completa
  - [x] Query params: start_date, end_date
  - [x] Retorna blocos de gravação
  - [x] Cache automático
- [x] `GET /timeline/{camera_id}/blocks` - Blocos específicos
  - [x] Granularidade por hora/dia
  - [x] Metadados de cada bloco
- [x] `GET /video/{camera_id}/{timestamp}` - Vídeo por timestamp
  - [x] Resolve timestamp para arquivo correto
  - [x] Retorna URL ou redirect
- [x] `POST /reindex/{camera_id}` - Força reindexação
  - [x] Limpa cache
  - [x] Reescaneia diretório
  - [x] Retorna status

### 📊 Models Timeline
- [x] `TimelineBlock`
  - [x] start_time, end_time
  - [x] file_path, file_size
  - [x] duration, fps
  - [x] has_audio, resolution
- [x] `CameraIndex`
  - [x] camera_id
  - [x] last_scan, total_files
  - [x] total_size, date_range
  - [x] blocks: List[TimelineBlock]

### 🔄 Background Tasks
- [x] Scan automático periódico
- [x] Detecção de novos arquivos
- [x] Cleanup de cache expirado
- [x] Health check de arquivos

### 📈 Algoritmos
- [x] **Timestamp Resolution**
  - [x] Busca binária por timestamp
  - [x] Interpolação entre arquivos
  - [x] Fallback para arquivo mais próximo
- [x] **Block Generation**
  - [x] Agrupa arquivos contíguos
  - [x] Detecta gaps na gravação
  - [x] Calcula estatísticas por bloco
- [x] **Incremental Indexing**
  - [x] Detecta apenas arquivos novos
  - [x] Merge com índice existente
  - [x] Otimização de performance

### 🗂 Estrutura de Dados
```python
# Exemplo de timeline response
{
  "camera_id": 1,
  "date_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-02T00:00:00Z"
  },
  "blocks": [
    {
      "start_time": "2024-01-01T08:00:00Z",
      "end_time": "2024-01-01T09:00:00Z",
      "duration": 3600,
      "file_count": 12,
      "total_size": 1073741824,
      "has_gaps": false
    }
  ],
  "stats": {
    "total_duration": 86400,
    "coverage_percent": 95.5,
    "total_files": 288,
    "total_size": 25769803776
  }
}
```

### ⚡ Performance
- [x] Cache em memória com Redis (opcional)
- [x] Índices otimizados por timestamp
- [x] Lazy loading de metadados
- [x] Paginação de resultados grandes

### 🔍 Utilitários FFmpeg
- [x] `ffprobe_wrapper.py`
  - [x] get_video_duration()
  - [x] get_video_resolution()
  - [x] get_video_fps()
  - [x] extract_thumbnail()

### ✅ Testes
- [x] Indexação de diretório funciona
- [x] Timeline gerada corretamente
- [x] Timestamp resolution precisa
- [x] Cache funciona corretamente
- [x] Performance aceitável (< 2s para 1 dia)

## Critérios de Aceite
- [x] Timeline carrega em < 2 segundos
- [x] Timestamp resolution com precisão de segundos
- [x] Cache reduz tempo de resposta em 80%
- [x] Suporta gaps na gravação
- [x] Metadados corretos (duração, tamanho, etc)

## Estimativa: 8 horas