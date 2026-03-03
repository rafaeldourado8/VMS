# 🔧 HAProxy Security - Troubleshooting

## 🔍 Verificar Configuração

### Validar sintaxe do haproxy.cfg
```bash
docker exec haproxy haproxy -c -f /usr/local/etc/haproxy/haproxy.cfg
```

### Ver configuração ativa
```bash
docker exec haproxy cat /usr/local/etc/haproxy/haproxy.cfg
```

## 📊 Monitoramento em Tempo Real

### Ver logs do HAProxy
```bash
# Logs em tempo real
docker logs -f haproxy

# Últimas 100 linhas
docker logs --tail 100 haproxy

# Filtrar por erro
docker logs haproxy 2>&1 | findstr "error"
```

### Estatísticas via CLI
```bash
# Conectar ao socket do HAProxy
docker exec -it haproxy sh

# Dentro do container
echo "show info" | socat stdio /var/run/haproxy.sock
echo "show stat" | socat stdio /var/run/haproxy.sock
echo "show table" | socat stdio /var/run/haproxy.sock
```

## 🚨 Problemas Comuns

### 1. Rate Limit Muito Agressivo

**Sintoma**: Usuários legítimos sendo bloqueados (429)

**Solução**: Ajustar limite no `haproxy.cfg`
```haproxy
# Aumentar de 200 para 500 req/10s
http-request deny deny_status 429 if { sc_http_req_rate(0) gt 500 }
```

### 2. Timeout Muito Curto

**Sintoma**: Requisições lentas falhando

**Solução**: Aumentar timeouts
```haproxy
timeout client  60s  # Era 30s
timeout server  60s  # Era 30s
```

### 3. Certificado SSL Inválido

**Sintoma**: Erro SSL ao acessar HTTPS

**Verificar certificado**:
```bash
# Ver detalhes do certificado
openssl x509 -in haproxy/certs/cert.pem -text -noout

# Verificar validade
openssl x509 -in haproxy/certs/cert.pem -noout -dates
```

**Gerar novo certificado self-signed**:
```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout haproxy/certs/cert.pem \
  -out haproxy/certs/cert.pem \
  -days 365 -subj "/CN=localhost"
```

### 4. Stats Page Não Acessível

**Sintoma**: Não consegue acessar http://localhost:8404/stats

**Verificar**:
```bash
# Porta está exposta?
docker ps | findstr haproxy

# Testar conexão
curl -I http://localhost:8404/stats
```

**Solução**: Verificar docker-compose.yml
```yaml
ports:
  - "8404:8404"  # Deve estar presente
```

### 5. Headers de Segurança Não Aparecem

**Sintoma**: curl não mostra headers de segurança

**Verificar**:
```bash
# Testar diretamente
curl -Ik https://localhost/ | findstr "X-Frame-Options"
```

**Solução**: Verificar se está em `defaults` ou `frontend`
```haproxy
defaults
    http-response set-header X-Frame-Options SAMEORIGIN
```

## 🧪 Testes de Segurança

### Teste de Penetração Básico

#### 1. SQL Injection (deve ser bloqueado pelo backend)
```bash
curl "https://localhost/api/cameras/?id=1' OR '1'='1" -k
```

#### 2. XSS (headers devem proteger)
```bash
curl "https://localhost/?search=<script>alert('xss')</script>" -k
```

#### 3. Path Traversal
```bash
curl "https://localhost/../../etc/passwd" -k
```

#### 4. Slowloris Attack (deve timeout)
```bash
# Enviar requisição lenta
(echo -n "GET / HTTP/1.1\r\nHost: localhost\r\n"; sleep 15; echo -e "\r\n") | nc localhost 80
```

### Ferramentas de Teste

#### OWASP ZAP
```bash
# Scan básico
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://localhost
```

#### Nikto
```bash
nikto -h https://localhost -ssl
```

#### SSLyze
```bash
sslyze --regular localhost:443
```

## 📈 Métricas Importantes

### Via Stats Page (http://localhost:8404/stats)

Monitorar:
- **Request Rate**: Requisições por segundo
- **Session Rate**: Novas sessões por segundo
- **Error Rate**: Taxa de erros 4xx/5xx
- **Queue**: Requisições em fila
- **Response Time**: Tempo de resposta médio

### Via Logs

Padrões a observar:
```bash
# Contar 429 (rate limit)
docker logs haproxy 2>&1 | findstr "429" | find /c /v ""

# Contar 5xx (erros de servidor)
docker logs haproxy 2>&1 | findstr "5[0-9][0-9]" | find /c /v ""

# IPs mais ativos
docker logs haproxy 2>&1 | findstr /R "[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*" | sort | uniq -c | sort -rn | head -10
```

## 🔐 Hardening Adicional

### 1. Limitar Tamanho de Requisição
```haproxy
# Adicionar no frontend
http-request deny deny_status 413 if { req.body_size gt 10485760 }  # 10MB
```

### 2. Blacklist de IPs
```haproxy
# Criar ACL com IPs bloqueados
acl blocked_ips src 1.2.3.4 5.6.7.8
http-request deny deny_status 403 if blocked_ips
```

### 3. Whitelist para Admin
```haproxy
# Apenas IPs específicos podem acessar /admin
acl is_admin path_beg /admin
acl admin_ips src 192.168.1.100 192.168.1.101
http-request deny deny_status 403 if is_admin !admin_ips
```

### 4. Rate Limit por Endpoint
```haproxy
# Rate limit mais agressivo para login
acl is_login path /api/auth/login
http-request deny deny_status 429 if is_login { sc_http_req_rate(0) gt 10 }
```

## 🚀 Performance vs Segurança

### Ajustar para Alta Performance
```haproxy
# Aumentar limites
maxconn 16384
timeout connect 3s
timeout client 20s
timeout server 20s

# Rate limit mais permissivo
http-request deny deny_status 429 if { sc_http_req_rate(0) gt 1000 }
```

### Ajustar para Máxima Segurança
```haproxy
# Limites mais restritivos
maxconn 4096
timeout connect 5s
timeout client 15s
timeout server 15s

# Rate limit mais agressivo
http-request deny deny_status 429 if { sc_http_req_rate(0) gt 50 }
```

## 📞 Suporte

### Logs Úteis para Debug
```bash
# Exportar logs para análise
docker logs haproxy > haproxy_debug.log 2>&1

# Ver configuração completa
docker exec haproxy haproxy -vv
```

### Informações do Sistema
```bash
# Versão do HAProxy
docker exec haproxy haproxy -v

# Recursos disponíveis
docker exec haproxy haproxy -vv | findstr "Built"
```

## ✅ Checklist de Troubleshooting

Quando algo não funciona:

1. [ ] Verificar logs: `docker logs haproxy`
2. [ ] Validar configuração: `haproxy -c -f haproxy.cfg`
3. [ ] Testar conectividade: `curl -I http://localhost/`
4. [ ] Verificar portas: `docker ps | findstr haproxy`
5. [ ] Checar certificado: `openssl x509 -in cert.pem -text`
6. [ ] Ver stats: `http://localhost:8404/stats`
7. [ ] Testar rate limit: Script de teste
8. [ ] Verificar headers: `curl -Ik https://localhost/`
9. [ ] Reiniciar serviço: `docker-compose restart haproxy`
10. [ ] Verificar .env: Variáveis HAPROXY_STATS_*
