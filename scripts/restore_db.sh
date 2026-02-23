#!/bin/bash

if [ -z "$1" ]; then
    echo "Uso: ./restore_db.sh <arquivo_backup.sql.gz>"
    echo ""
    echo "Backups disponíveis:"
    ls -lh /home/ubuntu/backups/*.sql.gz 2>/dev/null || echo "Nenhum backup encontrado"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Erro: Arquivo $BACKUP_FILE não encontrado"
    exit 1
fi

echo "=== ATENÇÃO: Restauração de Banco de Dados ==="
echo "Arquivo: $BACKUP_FILE"
echo ""
echo "Isso irá SUBSTITUIR todos os dados atuais!"
read -p "Deseja continuar? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Operação cancelada"
    exit 0
fi

echo ""
echo "Parando serviços..."
docker-compose stop backend lpr-service onvif-service recording-service

echo "Restaurando banco de dados..."
gunzip < $BACKUP_FILE | docker-compose exec -T postgres-primary psql -U vms_user vms_dev

if [ $? -eq 0 ]; then
    echo "✓ Restauração concluída com sucesso"
else
    echo "✗ Erro na restauração"
    exit 1
fi

echo "Reiniciando serviços..."
docker-compose up -d

echo ""
echo "=== Restauração finalizada ==="
echo "Aguarde alguns segundos para os serviços iniciarem"
