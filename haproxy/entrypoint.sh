#!/bin/sh
set -e

# Substituir variáveis de ambiente no template
envsubst < /usr/local/etc/haproxy/haproxy.cfg > /tmp/haproxy.cfg

# Iniciar HAProxy
exec haproxy -f /tmp/haproxy.cfg "$@"
