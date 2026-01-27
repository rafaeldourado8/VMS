#!/bin/bash

echo "=== Adicionando câmeras via API MediaMTX ==="

# Camera RTSP
curl -X POST http://localhost:9997/v3/config/paths/add/camera_rtsp \
  -H "Content-Type: application/json" \
  -d '{
    "source": "rtsp://admin:Camerite123@45.236.226.71:6047/cam/realmonitor?channel=1&subtype=0",
    "sourceOnDemand": false
  }'

echo ""

# Camera RTMP
curl -X POST http://localhost:9997/v3/config/paths/add/camera_rtmp \
  -H "Content-Type: application/json" \
  -d '{
    "source": "rtmp://inst-t4ntf-srs-rtmp-intelbras.camerite.services:1935/record/7KOM2715717FV.stream",
    "sourceOnDemand": false
  }'

echo ""

# Camera IP
curl -X POST http://localhost:9997/v3/config/paths/add/camera_ip \
  -H "Content-Type: application/json" \
  -d '{
    "source": "rtsp://138.255.75.231:503",
    "sourceOnDemand": false
  }'

echo ""
echo "=== Câmeras adicionadas ==="
echo "Acesse: http://localhost"
