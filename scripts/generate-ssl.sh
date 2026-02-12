#!/bin/bash

# Cria diretório para certificados
mkdir -p haproxy/certs

# Gera certificado autoassinado (válido por 365 dias)
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout haproxy/certs/key.pem \
  -out haproxy/certs/cert.pem \
  -days 365 \
  -subj "/C=BR/ST=State/L=City/O=Organization/CN=localhost"

# Combina certificado e chave em um único arquivo (formato HAProxy)
cat haproxy/certs/cert.pem haproxy/certs/key.pem > haproxy/certs/cert.pem

echo "✅ Certificado SSL gerado em haproxy/certs/cert.pem"
echo "⚠️  ATENÇÃO: Este é um certificado autoassinado para desenvolvimento"
echo "⚠️  Para produção, use Let's Encrypt (certbot) ou um certificado válido"
