#!/bin/bash
set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"
S3_BUCKET="vms-dev-backups-239857123540"

mkdir -p $BACKUP_DIR

echo "Starting backup at $TIMESTAMP..."

# Backup PostgreSQL
docker-compose exec -T postgres_db pg_dump -U ${POSTGRES_USER:-gtvision_user} ${POSTGRES_DB:-gtvision_db} | gzip > $BACKUP_DIR/db_$TIMESTAMP.sql.gz

# Upload to S3
if command -v aws &> /dev/null; then
    echo "Uploading to S3..."
    aws s3 cp $BACKUP_DIR/db_$TIMESTAMP.sql.gz s3://$S3_BUCKET/dev/
    echo "Uploaded to S3: s3://$S3_BUCKET/dev/db_$TIMESTAMP.sql.gz"
fi

# Keep only last 7 days locally
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: db_$TIMESTAMP.sql.gz"
