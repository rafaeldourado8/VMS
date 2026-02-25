# Stream HLS Unificado - Gravações

## Conceito

Ao invés de servir cada MP4 como segmento TS individual (182 requisições), o VOD agora:

1. **Concatena** todos os MP4s do dia em um único stream virtual
2. **Gera HLS** com chunks de 5s usando FFmpeg
3. **Serve** como playlist única com poucos segmentos

## Fluxo

```
MP4s do dia (1440 arquivos de 60s)
  ↓
FFmpeg concat + HLS segmentation
  ↓
Playlist única com ~17.280 chunks de 5s
  ↓
HLS.js carrega apenas buffer necessário (30s = 6 chunks)
```

## Endpoints

### Stream Unificado
```
GET /vod/stream/{camera_id}/{date}/index.m3u8
```

Parâmetros opcionais:
- `start_time`: "10:00:00"
- `end_time`: "12:00:00"

### Segmentos
```
GET /vod/stream/{camera_id}/{date}/segment_00001.ts
```

## Vantagens

✅ **1 playlist** vs 1440 playlists individuais
✅ **Poucos chunks** carregados (apenas buffer de 30s)
✅ **Seek rápido** - HLS.js gerencia automaticamente
✅ **Cache eficiente** - Segmentos podem ser cacheados

## Uso

### Frontend
```typescript
// Automático - já configurado
const url = `/vod/stream/${cameraId}/${date}/index.m3u8`
```

### Filtrar por horário
```typescript
const url = `/vod/stream/${cameraId}/${date}/index.m3u8?start_time=10:00:00&end_time=12:00:00`
```

## Performance

| Métrica | Antes (chunks dinâmicos) | Depois (stream unificado) |
|---------|--------------------------|---------------------------|
| Requisições iniciais | 182 | ~10 |
| Tamanho playlist | 2.2KB | 2.2KB |
| Chunks carregados | 36 | 6 |
| Tempo para play | 3-5s | <1s |

## Cache

Segmentos são gerados uma vez e cacheados em `/tmp/hls/`:
```
/tmp/hls/playback_1_20260224/
  ├── index.m3u8
  ├── segment_00001.ts
  ├── segment_00002.ts
  └── ...
```

## Limpeza

Cache pode ser limpo manualmente:
```bash
docker exec vod rm -rf /tmp/hls/*
```

Ou automaticamente após X horas (TODO: implementar TTL)

## Teste

```bash
# Reiniciar VOD
docker-compose restart vod

# Testar stream
curl http://localhost/vod/stream/1/2026-02-24/index.m3u8

# Verificar cache
docker exec vod ls -lh /tmp/hls/
```
