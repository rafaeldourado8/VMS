#!/bin/bash

# Se algum comando falhar, o script para
set -e

echo "Aguardando PostgreSQL em $DB_HOST:$DB_PORT..."

# Loop simples com python para verificar se a porta do banco está aberta
# Isso é mais leve e compatível do que instalar netcat (nc) em imagens slim
until python -c "import socket; s = socket.socket(); s.settimeout(2); s.connect(('$DB_HOST', int('$DB_PORT'))); s.close();" 2>/dev/null; do
  echo "PostgreSQL indisponível - dormindo 2s..."
  sleep 2
done

echo "PostgreSQL está pronto!"

# Executa o comando passado para o container
exec "$@"