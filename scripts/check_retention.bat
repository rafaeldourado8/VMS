@echo off
echo ========================================
echo VERIFICANDO STATUS DE RETENCAO
echo ========================================
echo.

curl -s http://localhost:8003/recordings/retention-status | python -m json.tool

echo.
echo ========================================
echo ESTATISTICAS DO STORAGE
echo ========================================
echo.

curl -s http://localhost:8003/recordings/stats | python -m json.tool

echo.
pause
