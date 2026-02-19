@echo off
REM Script para configurar replicação PostgreSQL no Windows

echo Configurando replicação PostgreSQL...

REM Criar usuário de replicação no primary
docker exec -it gtvision_postgres_primary psql -U gtvision_user -d gtvision_db -c "CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'repl_password';"
docker exec -it gtvision_postgres_primary psql -U gtvision_user -d gtvision_db -c "SELECT pg_create_physical_replication_slot('replica_1_slot');"
docker exec -it gtvision_postgres_primary psql -U gtvision_user -d gtvision_db -c "SELECT pg_create_physical_replication_slot('replica_2_slot');"

REM Adicionar entrada no pg_hba.conf
docker exec -it gtvision_postgres_primary bash -c "echo 'host replication replicator all md5' >> /var/lib/postgresql/data/pg_hba.conf"

REM Recarregar configuração
docker exec -it gtvision_postgres_primary psql -U gtvision_user -c "SELECT pg_reload_conf();"

echo Replicação configurada com sucesso!
echo Verificar status: docker exec gtvision_postgres_primary psql -U gtvision_user -c "SELECT * FROM pg_stat_replication;"
pause
