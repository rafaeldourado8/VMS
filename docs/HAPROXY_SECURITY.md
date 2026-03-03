# 🔐 Segurança HAProxy

## ✅ Checklist de Segurança Implementado

### Local (Desenvolvimento)

- [x] **Rate limit global contra flood**
  - 200 requisições por 10 segundos por IP
  - Retorna HTTP 429 quando excedido
  - Configurado via `stick-table` com rastreamento por IP

- [x] **Timeout configurado**
  - `timeout connect 5s` - Conexão com backend
  - `timeout client 30s` - Inatividade do cliente
  - `timeout server 30s` - Inatividade do servidor
  - `timeout tunnel 3600s` - WebSocket/streaming
  - `timeout http-request 10s` - Proteção contra slowloris
  - `timeout http-keep-alive 5s` - Keep-alive

- [x] **Limite de conexões por IP**
  - Máximo de 100 conexões simultâneas por IP
  - Retorna HTTP 429 quando excedido
  - Rastreado via `stick-table` com `conn_cur`

- [x] **Headers de segurança globais**
  - `X-Frame-Options: SAMEORIGIN` - Proteção contra clickjacking
  - `X-Content-Type-Options: nosniff` - Previne MIME sniffing
  - `X-XSS-Protection: 1; mode=block` - Proteção XSS
  - `Referrer-Policy: strict-origin-when-cross-origin` - Controle de referrer
  - `Permissions-Policy` - Restringe APIs do navegador
  - Remove headers `Server` e `X-Powered-By` - Oculta versões

- [x] **Admin stats (8404) protegido**
  - Autenticação básica via variáveis de ambiente
  - Restrição por IP (localhost + rede Docker)
  - Acesso apenas em redes confiáveis

### Produção

- [x] **SSL termina no HAProxy**
  - Bind na porta 443 com certificado
  - Suporte HTTP/2 via ALPN
  - TLS mínimo: TLSv1.2
  - Ciphers seguros (ECDHE-AES-GCM)

- [x] **Redirecionar HTTP → HTTPS**
  - Redirect 301 automático
  - Todas requisições HTTP vão para HTTPS

- [x] **HSTS habilitado**
  - `max-age=31536000` (1 ano)
  - `includeSubDomains` - Aplica a subdomínios
  - `preload` - Elegível para lista de preload

### Proteções Adicionais

- [x] **Proteção contra métodos HTTP inválidos**
  - Bloqueia TRACE e CONNECT
  - Retorna HTTP 405

- [x] **Proteção contra headers maliciosos**
  - Valida unicidade de Host header
  - Valida unicidade de Content-Length
  - Retorna HTTP 400 em caso de duplicação

- [x] **Otimizações de conexão**
  - `option http-server-close` - Fecha conexões após resposta
  - `option forwardfor` - Preserva IP real do cliente

## 📊 Monitoramento

Acesse as estatísticas em: `http://localhost:8404/stats`

Credenciais configuradas via:
- `HAPROXY_STATS_USER`
- `HAPROXY_STATS_PASSWORD`

## 🔧 Configuração de Certificados

Certificados SSL devem estar em:
```
haproxy/certs/cert.pem
```

O arquivo deve conter:
1. Chave privada
2. Certificado
3. Certificados intermediários (se houver)

### Gerar certificado self-signed (desenvolvimento):
```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout haproxy/certs/cert.pem \
  -out haproxy/certs/cert.pem \
  -days 365 -subj "/CN=localhost"
```

## 🚀 Próximos Passos (Produção)

1. **Certificado válido**: Substituir self-signed por Let's Encrypt ou certificado comercial
2. **WAF**: Considerar ModSecurity ou AWS WAF
3. **DDoS**: Cloudflare ou AWS Shield
4. **Logs centralizados**: ELK Stack ou CloudWatch
5. **Alertas**: Configurar alertas para rate limit e erros 5xx

## 📝 Variáveis de Ambiente Necessárias

```env
HAPROXY_STATS_USER=admin
HAPROXY_STATS_PASSWORD=senha_forte_aqui
```

## 🔍 Testes de Segurança

### Testar rate limit:
```bash
for i in {1..250}; do curl -s http://localhost/ > /dev/null; done
```

### Testar HTTPS redirect:
```bash
curl -I http://localhost/
# Deve retornar 301 com Location: https://
```

### Testar HSTS:
```bash
curl -I https://localhost/
# Deve conter: Strict-Transport-Security
```

### Testar headers de segurança:
```bash
curl -I https://localhost/
# Verificar presença de X-Frame-Options, X-Content-Type-Options, etc.
```
