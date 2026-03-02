# Problemas de Infraestrutura

## 🔴 Crítico

### 1. Containers Rodando como Root
**Impacto:** Escalação de privilégios, comprometimento do host

**Ação Requerida:**
```dockerfile
# Adicionar em TODOS os Dockerfiles
RUN adduser -D -u 1000 appuser
USER appuser
```

### 2. Secrets em docker-compose.yml
**Impacto:** Exposição de credenciais no repositório

**Ação Requerida:**
- Usar Docker secrets ou variáveis de ambiente
- Mover credenciais para .env
- Adicionar .env ao .gitignore

### 3. Configurações Inseguras de Nginx
**Problemas:**
- Falta de SSL/TLS
- Headers de segurança ausentes
- Timeouts inadequados

**Ação Requerida:**
```nginx
# Adicionar headers de segurança
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000" always;
```

## 🟠 Alto

### 4. Falta de Health Checks
**Ação Requerida:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 5. Volumes sem Permissões Adequadas
**Ação Requerida:**
```yaml
volumes:
  - ./recordings:/recordings:rw
  - ./logs:/logs:rw
```

### 6. Network Policies Ausentes
**Ação Requerida:**
- Criar networks isoladas
- Limitar comunicação entre serviços
- Usar internal networks

## 📋 Checklist

- [ ] Containers não rodam como root
- [ ] Health checks configurados
- [ ] Secrets em vault
- [ ] SSL/TLS configurado
- [ ] Headers de segurança
- [ ] Network policies
- [ ] Resource limits
- [ ] Logging centralizado
