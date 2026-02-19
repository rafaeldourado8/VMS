# VOD HLS Service

Serviço que converte gravações MP4 para HLS on-demand.

## Funcionalidades

- Converte MP4 para HLS automaticamente
- Cache de segmentos HLS
- Não re-encode (usa copy codec)
- CORS habilitado
- Health check endpoint

## Endpoints

- `GET /health` - Health check
- `GET /vod/{camera_id}/{date}/{filename}.mp4/index.m3u8` - Playlist HLS
- `GET /vod/{camera_id}/{date}/{filename}.mp4/segment{N}.ts` - Segmento HLS

## Uso

### Docker (Recomendado)

```bash
cd services/vod
docker-compose up -d
```

### Local

```bash
cd services/vod
pip install -r requirements.txt
python main.py
```

## Variáveis de Ambiente

- `RECORDINGS_DIR` - Diretório das gravações (padrão: `/recordings`)
- `HLS_CACHE_DIR` - Diretório do cache HLS (padrão: `/hls_cache`)

## Exemplo

```
http://localhost:8004/vod/1/2026-02-16/12-44-27.mp4/index.m3u8
```
