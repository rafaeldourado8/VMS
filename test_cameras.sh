#!/bin/bash
# Script para publicar câmeras reais no MediaMTX

# Câmera 1
ffmpeg -rtsp_transport tcp -i "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0" \
  -c copy -f rtsp rtsp://localhost:8554/cam_1 &

# Câmera 2
ffmpeg -rtsp_transport tcp -i "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0" \
  -c copy -f rtsp rtsp://localhost:8554/cam_2 &

# Câmera 3
ffmpeg -rtsp_transport tcp -i "rtsp://admin:Camerite123@45.236.226.74:6050/cam/realmonitor?channel=1&subtype=0" \
  -c copy -f rtsp rtsp://localhost:8554/cam_3 &

# Câmera 4
ffmpeg -rtsp_transport tcp -i "rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0" \
  -c copy -f rtsp rtsp://localhost:8554/cam_4 &

# Câmera 5
ffmpeg -rtsp_transport tcp -i "rtsp://admin:Camerite123@45.236.226.71:6046/cam/realmonitor?channel=1&subtype=0" \
  -c copy -f rtsp rtsp://localhost:8554/cam_5 &

# Câmera 6
ffmpeg -rtsp_transport tcp -i "rtsp://admin:Camerite123@45.236.226.70:6045/cam/realmonitor?channel=1&subtype=0" \
  -c copy -f rtsp rtsp://localhost:8554/cam_6 &

echo "6 câmeras publicadas no MediaMTX"
echo "Acesse: http://localhost/hls/cam_1/index.m3u8"
