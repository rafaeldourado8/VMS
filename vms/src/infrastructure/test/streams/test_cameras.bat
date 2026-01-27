@echo off
echo === VMS - Teste de Streams ===
echo.

echo 1. Testando RTSP Camera...
start /B ffmpeg -i "rtsp://admin:Camerite123@45.236.226.71:6047/cam/realmonitor?channel=1&subtype=0" -c copy -f rtsp rtsp://localhost:8554/camera_rtsp
timeout /t 3 /nobreak >nul

echo 2. Testando RTMP Stream...
start /B ffmpeg -i "rtmp://inst-t4ntf-srs-rtmp-intelbras.camerite.services:1935/record/7KOM2715717FV.stream" -c copy -f rtsp rtsp://localhost:8554/camera_rtmp
timeout /t 3 /nobreak >nul

echo 3. Testando IP Camera...
start /B ffmpeg -i "rtsp://138.255.75.231:503" -c copy -f rtsp rtsp://localhost:8554/camera_ip
timeout /t 3 /nobreak >nul

echo.
echo === Streams publicados no MediaMTX ===
echo RTSP: http://localhost/hls/camera_rtsp/index.m3u8
echo RTMP: http://localhost/hls/camera_rtmp/index.m3u8
echo IP:   http://localhost/hls/camera_ip/index.m3u8
echo.
echo Abra http://localhost e teste os streams
echo Pressione qualquer tecla para parar...
pause >nul

taskkill /F /IM ffmpeg.exe
