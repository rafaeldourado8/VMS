# Snapshot Worker

Worker assíncrono para gerar snapshots das câmeras e publicar no Redis.

## Funcionalidades

- Extrai 1 frame a cada 30 segundos de cada câmera ativa
- Publica snapshots no Redis via `SnapshotCache`
- Suporta múltiplas câmeras simultâneas
- Processamento assíncrono com asyncio
- TTL de 60 segundos para cada snapshot no cache

## Uso

```python
from workers.snapshot_worker import SnapshotWorker

# Criar worker
worker = SnapshotWorker(redis_url="redis://localhost:6379")

# Adicionar câmeras
worker.add_camera("1", "rtsp://camera1.example.com/stream")
worker.add_camera("2", "rtsp://camera2.example.com/stream")

# Iniciar processamento
await worker.start()

# Remover câmera
worker.remove_camera("1")

# Parar worker
await worker.stop()
```

## SnapshotCache

Cache de snapshots no Redis com TTL configurável.

```python
from workers.snapshot_worker import SnapshotCache
from redis import Redis

redis = Redis.from_url("redis://localhost:6379")
cache = SnapshotCache(redis, ttl=60)

# Salvar snapshot
cache.set("camera_1", image_bytes)
```

## Formato das chaves no Redis

- Chave: `snapshot:{camera_id}`
- Valor: bytes da imagem JPEG
- TTL: 60 segundos (padrão)

## Dependências

- redis>=5.0.1
- asyncio (built-in)

## Configuração

- **Intervalo de snapshot**: 30 segundos (hardcoded)
- **TTL do cache**: 60 segundos (configurável)
- **Timeout de extração**: 10 segundos
- **Formato de saída**: JPEG (qualidade 5)

## Integração com FFmpeg

O worker usa FFmpeg para extrair frames:

```bash
ffmpeg -rtsp_transport tcp -i {rtsp_url} -frames:v 1 -f image2pipe -vcodec mjpeg -q:v 5 -
```

## Testes

Execute os testes unitários:

```bash
pytest tests/unit/test_snapshot_worker.py -v
```
