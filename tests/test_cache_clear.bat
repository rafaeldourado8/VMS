@echo off
echo ========================================
echo Teste de Limpeza de Cache de Thumbnails
echo ========================================
echo.

set API_URL=http://localhost/api
set TOKEN=

echo [1] Testando limpeza de cache de uma camera especifica...
curl -X POST "%API_URL%/thumbnails/1/clear/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json"
echo.
echo.

echo [2] Testando limpeza de todo o cache...
curl -X POST "%API_URL%/thumbnails/clear/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json"
echo.
echo.

echo ========================================
echo Teste concluido!
echo ========================================
pause
