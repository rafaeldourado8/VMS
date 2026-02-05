@echo off
echo === SPRINT 1: TESTE DE GRAVACAO ===
echo.

echo [1] Verificando gravacoes da camera 999...
curl -s http://localhost:8006/recordings/999 | python -m json.tool
echo.

echo [2] Validando integridade...
curl -s -X POST http://localhost:8006/recordings/999/validate | python -m json.tool
echo.

echo [3] Sincronizando com Django...
curl -s -X POST http://localhost:8000/api/recordings/sync_from_service/ ^
  -H "Content-Type: application/json" ^
  -d "{\"camera_id\": 999, \"date\": \"%date:~-4%-%date:~3,2%-%date:~0,2%\"}" | python -m json.tool
echo.

pause
