#!/bin/bash
set -e

# Criar usuário de replicação
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'replicator') THEN
            CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD '${POSTGRES_REPLICATION_PASSWORD}';
        END IF;
    END
    \$\$;
EOSQL

# Configurar pg_hba.conf para replicação
echo "host replication replicator all md5" >> ${PGDATA}/pg_hba.conf

# Criar slots de replicação
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT pg_create_physical_replication_slot('replica_1_slot') WHERE NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'replica_1_slot');
    SELECT pg_create_physical_replication_slot('replica_2_slot') WHERE NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'replica_2_slot');
EOSQL

echo "Replicação configurada com sucesso!"
