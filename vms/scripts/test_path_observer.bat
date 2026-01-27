@echo off
echo === Path Observer Test ===
echo.

echo [1] Verificar paths ativos...
curl -s http://localhost:9997/v3/paths/list
echo.
echo.

echo [2] Aguardar 15s para observer detectar...
ping -n 16 127.0.0.1 >nul

echo [3] Verificar logs do observer...
docker logs fastapi 2^>^&1 | findstr /I "PathObserver Path"
echo.
