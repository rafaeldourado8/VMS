#!/bin/bash
# Diagnóstico de Gravação VMS

echo "=== DIAGNÓSTICO VMS RECORDER ==="
echo ""

echo "1. Status do Recorder:"
docker top gtvision_recorder | grep ffmpeg | wc -l
echo ""

echo "2. Últimas gravações câmera 11:"
ls -lht /d/VMS/recordings/camera_11/2026-02-23/ | head -5
echo ""

echo "3. Últimas gravações câmera 12:"
ls -lht /d/VMS/recordings/camera_12/2026-02-23/ | head -5
echo ""

echo "4. Teste conexão MediaMTX cam_11:"
timeout 3 ffmpeg -i rtsp://localhost:8554/cam_11 -frames:v 1 -f null - 2>&1 | tail -3
echo ""

echo "5. Teste conexão MediaMTX cam_12:"
timeout 3 ffmpeg -i rtsp://localhost:8554/cam_12 -frames:v 1 -f null - 2>&1 | tail -3
echo ""

echo "6. Logs do Recorder (últimos erros):"
docker logs gtvision_recorder --tail 50 | grep -i "error\|travado\|morreu"
echo ""

echo "7. Status MediaMTX:"
curl -s http://localhost:9997/v3/paths/list | grep -E "cam_11|cam_12" -A 5
