#!/bin/bash
set -e

echo "Aguardando banco de dados..."
python wait_for_db.py

echo "Aplicando migrações..."
python manage.py migrate --noinput

echo "Iniciando clips worker..."
exec python manage.py process_clips
