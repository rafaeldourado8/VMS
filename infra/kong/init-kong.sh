#!/bin/sh
# Script de inicialização do Kong (caso precise migrar para DB mode no futuro)

set -e

echo "🚀 Iniciando Kong em DB-less mode..."

# Validar configuração
kong check /etc/kong/kong.yml

# Iniciar Kong
exec kong start --vv
