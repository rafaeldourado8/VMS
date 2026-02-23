@echo off
echo ========================================
echo Testando Frontend - HLS Integration
echo ========================================
echo.

echo [1/3] Verificando alteracoes no codigo...
echo.
echo Verificando api.ts...
findstr /C:"getPlaybackUrl" frontend\src\services\api.ts
findstr /C:"getHlsUrl" frontend\src\services\api.ts
echo.

echo Verificando RecordingPlayer.tsx...
findstr /C:"handlePlayRecording" frontend\src\components\cameras\RecordingPlayer.tsx
echo.

echo Verificando VideoPlayer.tsx...
findstr /C:"HLS VOD" frontend\src\components\cameras\VideoPlayer.tsx
echo.

echo ========================================
echo [2/3] Alteracoes Implementadas
echo ========================================
echo.
echo ✅ api.ts:
echo    - recordingService.list() usa /api/recordings/
echo    - recordingService.getHlsUrl() retorna URL HLS
echo    - recordingService.getPlaybackUrl() gera URL VOD
echo.
echo ✅ RecordingPlayer.tsx:
echo    - handlePlayRecording() usa HLS URL
echo    - Integrado com VideoPlayer HLS
echo.
echo ✅ VideoPlayer.tsx:
echo    - Suporte HLS nativo (ja existia)
echo    - Detecta .m3u8 automaticamente
echo    - Usa hls.js para playback
echo.

echo ========================================
echo [3/3] Como Testar
echo ========================================
echo.
echo 1. Reiniciar frontend:
echo    cd frontend
echo    npm run dev
echo.
echo 2. Acessar: http://localhost:5173
echo.
echo 3. Ir em Cameras ^> Gravacoes
echo.
echo 4. Selecionar data e clicar em Play
echo.
echo 5. Verificar no DevTools:
echo    - Network: requisicoes para /vod/*.m3u8
echo    - Console: logs do HLS player
echo.

echo ========================================
echo URLs de Teste
echo ========================================
echo.
echo Backend API:
echo   http://localhost/api/recordings/?camera_id=1
echo.
echo VOD Service:
echo   http://localhost/vod/camera_1/2026-02-20/12-44-27.mp4/index.m3u8
echo.
echo Frontend:
echo   http://localhost:5173
echo.

pause
