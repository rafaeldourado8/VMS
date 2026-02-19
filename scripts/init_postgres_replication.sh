#!/bin/bash
# Script para configurar replicação PostgreSQL

set -e

echo "🔧 Configurando replicação PostgreSQL..."

# Criar usuário de replicação no primary
docker exec -it gtvision_postgres_primary psql -U ${POSTGRES_USER:-gtvision_user} -d ${POSTGRES_DB:-gtvision_db} <<-EOSQL
    CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD '${POSTGRES_REPLICATION_PASSWORD:-repl_password}';
    SELECT pg_create_physical_replication_slot('replica_1_slot');
    SELECT pg_create_physical_replication_slot('replica_2_slot');
EOSQL

# Adicionar entrada no pg_hba.conf
docker exec -it gtvision_postgres_primary bash -c "echo 'host replication replicator all md5' >> /var/lib/postgresql/data/pg_hba.conf"

# Recarregar configuração
docker exec -it gtvision_postgres_primary psql -U ${POSTGRES_USER:-gtvision_user} -c "SELECT pg_reload_conf();"

echo "✅ Replicação configurada com sucesso!"
echo "📊 Verificar status: docker exec gtvision_postgres_primary psql -U ${POSTGRES_USER:-gtvision_user} -c 'SELECT * FROM pg_stat_replication;'"
