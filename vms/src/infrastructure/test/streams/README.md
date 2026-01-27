# Teste de Streams - VMS

## Testar

```bash
docker-compose up -d
```

O container `ffmpeg_test` vai adicionar as 3 câmeras via API do MediaMTX.

Abra: http://localhost e digite `camera_rtsp`, `camera_rtmp` ou `camera_ip`

## Adicionar manualmente

```bash
add_cameras.bat
```

## Verificar streams

```bash
curl http://localhost:9997/v3/paths/list
```

## Ver logs

```bash
docker logs -f vms_mediamtx_mvp
```
