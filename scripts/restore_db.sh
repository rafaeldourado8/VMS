#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: ./restore_db.sh <backup_file.sql.gz>"
    echo "Example: ./restore_db.sh db_20260302_120000.sql.gz"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "WARNING: This will restore database from $BACKUP_FILE"
echo "Current database will be dropped and recreated!"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo "Restoring database..."

# Drop and recreate database
docker-compose exec -T postgres_db psql -U ${POSTGRES_USER:-gtvision_user} -c "DROP DATABASE IF EXISTS ${POSTGRES_DB:-gtvision_db};"
docker-compose exec -T postgres_db psql -U ${POSTGRES_USER:-gtvision_user} -c "CREATE DATABASE ${POSTGRES_DB:-gtvision_db};"

# Restore from backup
gunzip < $BACKUP_FILE | docker-compose exec -T postgres_db psql -U ${POSTGRES_USER:-gtvision_user} ${POSTGRES_DB:-gtvision_db}

echo "Database restored successfully!"
