#!/bin/bash

# Configurações
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"
RETENTION_DAYS=7

# Criar diretório se não existir
mkdir -p $BACKUP_DIR

echo "=== Iniciando backup em $TIMESTAMP ==="

# Backup PostgreSQL Primary
echo "Fazendo backup do banco de dados..."
docker-compose exec -T postgres-primary pg_dump -U vms_user vms_dev | gzip > $BACKUP_DIR/db_$TIMESTAMP.sql.gz

if [ $? -eq 0 ]; then
    echo "✓ Backup do banco concluído: db_$TIMESTAMP.sql.gz"
    SIZE=$(du -h $BACKUP_DIR/db_$TIMESTAMP.sql.gz | cut -f1)
    echo "  Tamanho: $SIZE"
else
    echo "✗ Erro ao fazer backup do banco"
    exit 1
fi

# Backup de arquivos importantes
echo "Fazendo backup de configurações..."
tar -czf $BACKUP_DIR/config_$TIMESTAMP.tar.gz \
    .env \
    docker-compose.yml \
    config/ \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Backup de configurações concluído"
fi

# Upload para S3 (opcional - descomentar se configurado)
# if command -v aws &> /dev/null; then
#     echo "Enviando para S3..."
#     aws s3 cp $BACKUP_DIR/db_$TIMESTAMP.sql.gz s3://vms-backups/dev/
#     aws s3 cp $BACKUP_DIR/config_$TIMESTAMP.tar.gz s3://vms-backups/dev/
#     echo "✓ Upload para S3 concluído"
# fi

# Limpar backups antigos
echo "Limpando backups antigos (>$RETENTION_DAYS dias)..."
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "config_*.tar.gz" -mtime +$RETENTION_DAYS -delete
echo "✓ Limpeza concluída"

# Listar backups disponíveis
echo ""
echo "=== Backups disponíveis ==="
ls -lh $BACKUP_DIR | grep -E "db_|config_"

echo ""
echo "=== Backup finalizado com sucesso ==="
