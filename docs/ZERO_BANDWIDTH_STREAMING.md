# Streaming com Zero Desperdício de Banda

## Problema Atual

MP4 direto baixa o arquivo progressivamente. Se você:
- Abre vídeo de 1h (500MB)
- Assiste 5 minutos
- Fecha

**Banda consumida**: ~40-50MB (buffer do player)

## Solução: Streaming Adaptativo Real

### Opção 1: MSE (Media Source Extensions)

```typescript
// Frontend envia apenas timestamp desejado
const response = await fetch(`/recordings/stream?camera=1&date=2026-02-25&start=10:30:00&duration=30`)
const reader = response.body.getReader()

// Recebe apenas os 30s solicitados
while (true) {
  const { done, value } = await reader.read()
  if (done) break
  sourceBuffer.appendBuffer(value)
}
```

### Opção 2: Nginx Slice Module

```nginx
location /recordings/ {
    slice 1m;  # Fatias de 1MB
    proxy_cache_key $uri$is_args$args$slice_range;
    proxy_set_header Range $slice_range;
    proxy_cache_valid 200 206 1h;
}
```

### Opção 3: FFmpeg Streaming Service

```python
@app.get("/stream/{camera_id}/{date}")
async def stream_segment(camera_id: int, date: str, start: str, duration: int = 30):
    mp4_path = f"/recordings/camera_{camera_id}/{date}/{start}.mp4"
    
    cmd = [
        'ffmpeg', '-i', mp4_path,
        '-ss', start, '-t', str(duration),
        '-c', 'copy', '-f', 'mp4',
        '-movflags', 'frag_keyframe+empty_moov',
        'pipe:1'
    ]
    
    process = await asyncio.create_subprocess_exec(*cmd, stdout=PIPE)
    
    async def generate():
        while True:
            chunk = await process.stdout.read(65536)
            if not chunk: break
            yield chunk
    
    return StreamingResponse(generate(), media_type="video/mp4")
```

## Comparação

| Método | Banda (1h vídeo, 5min assistidos) | Seek | Complexidade |
|--------|-----------------------------------|------|--------------|
| MP4 Direto | ~50MB (buffer) | Rápido | Baixa |
| HLS | ~40MB (segmentos) | Médio | Média |
| MSE + Streaming | ~5MB (exato) | Instantâneo | Alta |
| Slice Module | ~10MB (cache) | Rápido | Média |

## Recomendação

Para **zero desperdício**:

1. **Curto prazo**: Adicionar `preload="metadata"` no `<video>`
   - Baixa apenas metadados (~100KB)
   - Só carrega vídeo ao dar play

2. **Médio prazo**: Implementar Slice Module no nginx
   - Fatias de 1MB
   - Cache inteligente

3. **Longo prazo**: MSE + Streaming Service
   - Controle total
   - Banda mínima
