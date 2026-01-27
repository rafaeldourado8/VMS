@echo off
setlocal enabledelayedexpansion

set CITY_ID=2ca65fec-ed93-40d1-bdf2-386a94e25fb1

echo === Iniciando 1 stream RTSP ===
echo Usando camera RTSP 01: rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1^&subtype=0
echo.
curl -s -X POST http://localhost:8001/api/streaming/start/0c4a7f3e-ec5f-4c5e-b5e5-d5e5e5e5e5e5 ^
  -H "Content-Type: application/json" ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1" > temp_rtsp.json

echo.
type temp_rtsp.json
echo.

for /f "tokens=2 delims=:, " %%a in ('findstr "session_id" temp_rtsp.json') do set SESSION_ID=%%~a

echo === Aguardando 5 segundos ===
ping -n 6 127.0.0.1 >nul

echo === Verificando path no MediaMTX ===
curl -s http://localhost:9997/v3/paths/list

echo.
echo === Testando HLS RTSP ===
curl -I http://localhost/hls/stream_%SESSION_ID%/index.m3u8

del temp_rtsp.json
