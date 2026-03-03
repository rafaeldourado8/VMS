#!/bin/sh
set -e

# Substituir variáveis de ambiente no template
envsubst < /etc/kong/kong.yml.template > /etc/kong/kong.yml

# Iniciar Kong
exec /docker-entrypoint.sh "$@"
