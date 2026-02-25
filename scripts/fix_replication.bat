@echo off
REM Script para corrigir replicação PostgreSQL

echo ========================================
echo Corrigindo replicação PostgreSQL...
echo ========================================

REM Criar usuário de replicação no primary
echo.
echo [1/5] Criando usuário replicator...
docker exec gtvision_postgres_primary psql -U gtvision_user -d gtvision_db -c "DROP USER IF EXISTS replicator;"
docker exec gtvision_postgres_primary psql -U gtvision_user -d gtvision_db -c "CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'repl_password';"

REM Criar slots de replicação
echo.
echo [2/5] Criando slots de replicação...
docker exec gtvision_postgres_primary psql -U gtvision_user -d gtvision_db -c "SELECT pg_drop_replication_slot('replica_1_slot') WHERE EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'replica_1_slot');" 2>nul
docker exec gtvision_postgres_primary psql -U gtvision_user -d gtvision_db -c "SELECT pg_drop_replication_slot('replica_2_slot') WHERE EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'replica_2_slot');" 2>nul
docker exec gtvision_postgres_primary psql -U gtvision_user -d gtvision_db -c "SELECT pg_create_physical_replication_slot('replica_1_slot');"
docker exec gtvision_postgres_primary psql -U gtvision_user -d gtvision_db -c "SELECT pg_create_physical_replication_slot('replica_2_slot');"

REM Adicionar entrada no pg_hba.conf
echo.
echo [3/5] Configurando pg_hba.conf...
docker exec gtvision_postgres_primary bash -c "grep -q 'host replication replicator' /var/lib/postgresql/data/pg_hba.conf || echo 'host replication replicator all md5' >> /var/lib/postgresql/data/pg_hba.conf"

REM Recarregar configuração
echo.
echo [4/5] Recarregando configuração...
docker exec gtvision_postgres_primary psql -U gtvision_user -c "SELECT pg_reload_conf();"

REM Reiniciar réplicas
echo.
echo [5/5] Reiniciando réplicas...
docker restart gtvision_postgres_replica_1 gtvision_postgres_replica_2

echo.
echo ========================================
echo Replicação corrigida!
echo ========================================
echo.
echo Aguarde 10 segundos e verifique o status:
timeout /t 10 /nobreak >nul
docker exec gtvision_postgres_primary psql -U gtvision_user -c "SELECT * FROM pg_stat_replication;"

pause
