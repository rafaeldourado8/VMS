@echo off
REM Script para consultar gravacoes no banco de dados (tabela correta)

echo ========================================
echo CONSULTA DE GRAVACOES - VMS
echo Tabela: recording_segments
echo ========================================
echo.

echo [1] Listar todas as gravacoes (ultimas 20)
docker exec gtvision_postgres psql -U gtvision_user -d gtvision_db -c "SELECT camera_id, file_path, start_time, duration_seconds, ROUND(file_size_bytes/1024.0/1024.0, 2) as size_mb FROM recording_segments ORDER BY start_time DESC LIMIT 20;"

echo.
echo [2] Contar gravacoes por camera
docker exec gtvision_postgres psql -U gtvision_user -d gtvision_db -c "SELECT camera_id, COUNT(*) as total, ROUND(SUM(file_size_bytes)/1024.0/1024.0, 2) as total_mb FROM recording_segments GROUP BY camera_id ORDER BY camera_id;"

echo.
echo [3] Gravacoes de hoje
docker exec gtvision_postgres psql -U gtvision_user -d gtvision_db -c "SELECT camera_id, file_path, start_time FROM recording_segments WHERE DATE(start_time) = CURRENT_DATE ORDER BY start_time;"

echo.
echo [4] Total de gravacoes
docker exec gtvision_postgres psql -U gtvision_user -d gtvision_db -c "SELECT COUNT(*) as total_recordings, ROUND(SUM(file_size_bytes)/1024.0/1024.0/1024.0, 2) as total_gb FROM recording_segments;"

echo.
echo ========================================
pause
