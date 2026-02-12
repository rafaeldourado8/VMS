@echo off
REM Script para consultar gravações no banco de dados

echo ========================================
echo CONSULTA DE GRAVACOES - VMS
echo ========================================
echo.

echo [1] Listar todas as gravacoes (ultimas 20)
docker exec -it gtvision_postgres psql -U gtvision_user -d gtvision_db -c "SELECT camera_id, date, file_name, size_mb, duration_min, is_valid, created_at FROM recordings ORDER BY created_at DESC LIMIT 20;"

echo.
echo [2] Contar gravacoes por camera
docker exec -it gtvision_postgres psql -U gtvision_user -d gtvision_db -c "SELECT camera_id, COUNT(*) as total, ROUND(SUM(size_mb)::numeric, 2) as total_mb FROM recordings GROUP BY camera_id ORDER BY camera_id;"

echo.
echo [3] Gravacoes de hoje
docker exec -it gtvision_postgres psql -U gtvision_user -d gtvision_db -c "SELECT camera_id, date, file_name, size_mb FROM recordings WHERE date = CURRENT_DATE ORDER BY file_name;"

echo.
echo [4] Verificar gravacoes invalidas
docker exec -it gtvision_postgres psql -U gtvision_user -d gtvision_db -c "SELECT camera_id, date, file_name FROM recordings WHERE is_valid = false;"

echo.
echo ========================================
pause
