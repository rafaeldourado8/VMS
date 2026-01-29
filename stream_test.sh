#!/bin/bash
# Stream test video to MediaMTX
ffmpeg -re -stream_loop -1 -i /app/1280_720_60fps.mp4 \
  -c:v libx264 -preset ultrafast -tune zerolatency \
  -b:v 2M -maxrate 2M -bufsize 4M \
  -g 60 -f rtsp rtsp://mediamtx:8554/test_video
