@echo off
setlocal enabledelayedexpansion

set CITY_ID=2ca65fec-ed93-40d1-bdf2-386a94e25fb1

echo === Iniciando 1 stream RTMP ===
curl -s -X POST http://localhost:8001/api/streaming/start/d7ebdaac-9d09-470f-a208-34ce2e4f9689 ^
  -H "Content-Type: application/json" ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1" > temp_session.json

echo.
type temp_session.json
echo.

for /f "tokens=2 delims=:, " %%a in ('findstr "session_id" temp_session.json') do set SESSION_ID=%%~a

echo === Aguardando 3 segundos ===
ping -n 4 127.0.0.1 >nul

echo === Verificando path no MediaMTX ===
curl -s http://localhost:9997/v3/paths/list

echo.
echo === Testando HLS ===
curl -I http://localhost/hls/stream_%SESSION_ID%/index.m3u8

del temp_session.json
