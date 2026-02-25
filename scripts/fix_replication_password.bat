@echo off
echo ========================================
echo Corrigindo senha do replicator
echo ========================================

docker exec -it gtvision_postgres_primary psql -U gtvision_user -d gtvision_db -c "ALTER USER replicator WITH PASSWORD 'repl_password';"

echo.
echo ========================================
echo Senha corrigida!
echo ========================================
pause
