@echo off
echo ========================================
echo Removendo réplicas PostgreSQL...
echo ========================================

docker stop gtvision_postgres_replica_1 gtvision_postgres_replica_2 2>nul
docker rm gtvision_postgres_replica_1 gtvision_postgres_replica_2 2>nul
docker volume rm vms_gtvision_pg_replica_1 vms_gtvision_pg_replica_2 2>nul

echo.
echo ========================================
echo Réplicas removidas com sucesso!
echo ========================================
echo.
echo Sistema agora opera apenas com PostgreSQL Primary.
echo Os erros de autenticação devem parar.
pause
