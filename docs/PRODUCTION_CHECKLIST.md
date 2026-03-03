# 🛡️ Checklist de Segurança e Estabilidade - VMS (300 Câmeras On-Demand)

## 📋 Visão Geral

Este checklist cobre todos os aspectos críticos de segurança, estabilidade e performance do VMS.

**IMPORTANTE**: Tudo deve funcionar **LOCALMENTE PRIMEIRO** antes de pensar em produção.

**Contexto**: Streamings são on-demand (nunca simultâneos), portanto testes de carga devem focar em transições sequenciais, não concorrência massiva.

---

## 🎯 Prioridade de Execução (LOCAL)

### FASE 1 - CRÍTICO (Fazer AGORA - Local)
1. ✅ Atualizar Django (resolver SQL injection alert)
2. ✅ Tirar `runserver` → Gunicorn (testar local)
3. ✅ Tirar `uvicorn` puro → Gunicorn + UvicornWorker (testar local)
4. ✅ Containers non-root
5. ✅ Fechar portas internas no docker-compose

### FASE 2 - SEGURANÇA (Validar Local)
6. ✅ Testar acesso a recordings (segurança)
7. ✅ Testar SQL injection local
8. ✅ Testar acesso cross-organization
9. ✅ Rate limiting básico
10. ✅ CORS correto

### FASE 3 - PERFORMANCE (Validar Local)
11. ✅ Testar startup de 10 streams sequenciais
12. ✅ Medir uso de recursos por stream
13. ✅ Testar transição rápida entre câmeras

### FASE 4 - PRODUÇÃO (Só depois de tudo funcionar local)
14. ✅ HAProxy com SSL
15. ✅ `DEBUG=False`
16. ✅ `ALLOWED_HOSTS` restrito
17. ✅ Separar docker-compose.dev.yml e .prod.yml

---

## 🛡️ 1. EDGE — HAPROXY (Camada Crítica)

### 🔐 Segurança

**Local:**
- [x] Rate limit global contra flood
- [x] Timeout configurado (connect, client, server)
- [x] Limite de conexões por IP
- [x] Headers de segurança globais
- [x] Admin stats (8404) protegido por auth/IP

**Produção (depois):**
- [x] SSL termina no HAProxy (comentado para dev)
- [x] Redirecionar HTTP → HTTPS (comentado para dev)
- [x] HSTS habilitado (comentado para dev)

### ⚙️ Estabilidade

- [ ] Healthcheck do Kong
- [ ] Healthcheck do Streaming
- [ ] Healthcheck do Nginx
- [ ] Failover configurado
- [ ] Log estruturado habilitado

**Arquivos**: `haproxy/haproxy.cfg`

---

## 🛡️ 2. KONG — API GATEWAY (Somente Django)

### 🔐 Segurança

- [ ] Admin API do Kong NÃO pública
- [ ] Rodando apenas interno
- [ ] Plugins revisados
- [ ] CORS restrito (não usar `origins=*`)
- [ ] Rate limit configurado corretamente
- [ ] Request size limit coerente
- [ ] Security headers configurados
- [ ] Não duplicar header com HAProxy

### ⚙️ Arquitetura

- [ ] Só recebe `/api/*` e `/admin/*`
- [ ] Não roteia static
- [ ] Não roteia streaming

**Arquivos**: `kong/kong.yml`

---

## 🛡️ 3. DJANGO (Backend Principal)

### 🔐 Segurança

**Local (fazer agora):**
- [ ] NÃO usar `runserver` (usar Gunicorn local)
- [ ] Gunicorn com workers adequados
- [ ] Atualizar Django (resolver SQL injection alert)
- [ ] Não usar raw SQL concatenado
- [ ] Validar permissões por role
- [ ] Rate limit no login
- [ ] Cookies `HttpOnly`
- [ ] `CSRF_TRUSTED_ORIGINS` definido

**Produção (depois):**
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` restrito
- [ ] Cookies `Secure`

### ⚙️ Estabilidade

- [ ] Healthcheck confiável
- [ ] Logging em stdout
- [ ] Timeout Gunicorn configurado
- [ ] Número de workers adequado ao CPU

**Arquivos**: `backend/Dockerfile`, `backend/config/settings.py`

---

## 🛡️ 4. FASTAPI (Streaming / Serviços)

### 🔐 Segurança

**Local (fazer agora):**
- [ ] Gunicorn + UvicornWorker (testar local)
- [ ] Autenticação obrigatória
- [ ] Validar inputs Pydantic
- [ ] Sem SQL manual

**Produção (depois):**
- [ ] Remover docs (`/docs`, `/redoc`)

### ⚙️ Performance

- [ ] Workers dimensionados (1-2 suficiente para on-demand)
- [ ] Timeout configurado
- [ ] Healthcheck funcional

**Arquivos**: `services/streaming/Dockerfile`, `services/streaming/main.py`

---

## 🛡️ 5. NGINX (Static + Recordings)

### 🔐 Segurança

**Local (fazer agora):**
- [ ] Limitar acesso a `/recordings` (autenticação)
- [ ] CORS configurado corretamente
- [ ] Range requests funcionando
- [ ] Buffer configurado adequadamente

**Produção (depois):**
- [ ] Não expor Nginx direto
- [ ] Apenas via HAProxy

### ⚙️ Performance

- [ ] `sendfile on`
- [ ] `tcp_nopush on`
- [ ] Cache configurado
- [ ] Testar seek em MP4

**Arquivos**: `nginx/nginx.conf`

---

## 🛡️ 6. MEDIAMTX (Streaming Core)

### 🔐 Segurança

**Local (fazer agora):**
- [ ] API 9997 NÃO exposta externamente
- [ ] Config protegida
- [ ] Limitar número máximo de conexões

**Produção (depois):**
- [ ] RTSP protegido (se público)

### ⚙️ Performance (On-Demand)

- [ ] Testar startup de 10 streams sequenciais
- [ ] Medir tempo de inicialização por stream
- [ ] Monitorar CPU por stream
- [ ] Monitorar memória por stream
- [ ] Monitorar IO por stream
- [ ] Monitorar banda por stream
- [ ] Testar transição rápida entre câmeras

**Arquivos**: `mediamtx.yml`

---

## 🛡️ 7. DOCKER HARDENING

- [ ] Containers NÃO rodam como root
- [ ] `no-new-privileges` habilitado
- [ ] Limite de CPU/memória definido
- [ ] Sem `privileged` mode
- [ ] Sem portas internas expostas
- [ ] Logs apenas stdout
- [ ] Volumes com permissão correta

**Arquivos**: `docker-compose.yml`, `docker-compose.prod.yml`

---

## 🛡️ 8. BANCO (POSTGRES)

- [ ] Porta 5432 não exposta
- [ ] Usuário não-superuser
- [ ] Senha forte
- [ ] Backup testado
- [ ] Healthcheck ativo
- [ ] Conexões limitadas

**Arquivos**: `docker-compose.yml`

---

## 🛡️ 9. REDIS

- [ ] Não expor porta
- [ ] Autenticação se necessário
- [ ] Monitorar memória
- [ ] Sem default config aberta

**Arquivos**: `docker-compose.yml`

---

## 🛡️ 10. STORAGE (Recordings / HLS / Snapshots)

- [ ] Fora do Git
- [ ] Permissões corretas
- [ ] Retenção automática testada
- [ ] Testar deleção segura
- [ ] Monitorar espaço em disco

**Diretórios**: `recordings/`, `hls_cache/`, `snapshots/`

---

## 🛡️ 11. TESTES DE SEGURANÇA LOCAL

- [ ] Testar SQL injection manual
- [ ] Testar brute force
- [ ] Testar token expirado
- [ ] Testar acesso direto a `/recordings`
- [ ] Testar acesso a recordings de outras organizações
- [ ] Testar acesso sem token válido
- [ ] Testar flood request
- [ ] Testar upload malicioso

**Scripts**: `backend/test_sql_injection.py`, `tests/test_security.py`

---

## 🛡️ 12. DEPENDÊNCIAS

- [ ] `pip-audit` limpo
- [ ] `npm audit` limpo
- [ ] Dependabot ativo
- [ ] Versões travadas

**Arquivos**: `backend/requirements.txt`, `frontend/package.json`

---

## 🛡️ 13. SIMULAÇÃO DE CARGA (On-Demand)

**Importante**: Como streamings são on-demand (nunca simultâneos), focar em:

- [ ] Simular 10 câmeras sequenciais
- [ ] Simular 30 câmeras sequenciais
- [ ] Medir tempo de startup do stream
- [ ] Medir latência de resposta ao iniciar stream
- [ ] Testar transição rápida entre câmeras (< 2s)
- [ ] Medir CPU MediaMTX por stream
- [ ] Medir IO disco por stream
- [ ] Medir banda por stream
- [ ] Medir latência HLS
- [ ] Calcular câmeras por node

**Scripts**: `backend/locustfile.py`, `tests/test_streaming_capacity.py`

---

## 🛡️ 14. SEPARAÇÃO DEV / PROD

**IMPORTANTE**: Fazer isso SÓ DEPOIS de tudo funcionar localmente.

### Criar Arquivos (Fase 4)

- [ ] `docker-compose.dev.yml` (atual docker-compose.yml)
- [ ] `docker-compose.prod.yml` (novo, hardened)

### DEV (Local - Atual)

- [x] Vite dev server
- [x] Hot reload habilitado
- [x] Debug habilitado
- [x] Portas expostas para debug

### PROD (Futuro)

- [ ] Gunicorn (já testar local antes)
- [ ] Sem reload
- [ ] Sem portas internas expostas
- [ ] Sem volumes de código
- [ ] Build otimizado do frontend

---

## 📊 Métricas de Sucesso (Local)

### Performance (Validar Local)
- Startup de stream: < 2s
- Latência HLS: < 5s
- CPU por stream: < 5%
- Memória por stream: < 100MB
- Transição entre câmeras: < 2s

### Segurança (Validar Local)
- 0 vulnerabilidades críticas (pip-audit, npm audit)
- 0 SQL injection possível
- 100% requests autenticados
- Acesso cross-organization bloqueado
- Rate limiting funcionando

### Estabilidade (Validar Local)
- Containers reiniciam corretamente
- Healthchecks: 100% pass
- Logs estruturados (stdout)
- Sem runserver/uvicorn puro
- Gunicorn funcionando local

---

## 🔗 Documentação Relacionada

- [DEPLOY_CHECKLIST.md](./DEPLOY_CHECKLIST.md) - Checklist de deploy
- [SECURITY_RECORDINGS_TODO.md](./SECURITY_RECORDINGS_TODO.md) - Segurança de recordings
- [LOAD_TESTING.md](./LOAD_TESTING.md) - Testes de carga
- [ARCHITECTURE_500_CAMERAS.md](./ARCHITECTURE_500_CAMERAS.md) - Arquitetura escalável

---

## 📝 Notas Importantes

- **TUDO deve funcionar LOCALMENTE primeiro**
- Não pule para produção sem validar local
- Itens críticos (FASE 1) são bloqueantes
- Testes de carga devem rodar local primeiro
- FASE 4 (produção) só depois de FASE 1-3 completas
- Documentar qualquer desvio do checklist com justificativa

## 🚀 Próximos Passos

1. Completar FASE 1 (crítico local)
2. Validar FASE 2 (segurança local)
3. Testar FASE 3 (performance local)
4. Só então pensar em FASE 4 (produção)
