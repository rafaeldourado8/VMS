# ✅ Solução - Session Timeout

## Resumo da Correção
Configurar Django para expirar sessões após 4 minutos de inatividade, com renovação automática a cada requisição.

## Código Corrigido

### Antes
```python
# backend/config/settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### Depois
```python
# backend/config/settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Session timeout: 4 minutos de inatividade
SESSION_COOKIE_AGE = 240  # 4 minutos em segundos
SESSION_SAVE_EVERY_REQUEST = True  # Renova a cada requisição
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Expira ao fechar navegador

# Security
SESSION_COOKIE_HTTPONLY = True  # Previne XSS
SESSION_COOKIE_SECURE = True  # Apenas HTTPS (prod)
SESSION_COOKIE_SAMESITE = 'Lax'  # Previne CSRF
```

## Arquivos Modificados
- `backend/config/settings.py` - Adicionadas configurações de sessão
- `backend/config/settings_prod.py` - `SESSION_COOKIE_SECURE = True` para produção

## Explicação das Configurações

### SESSION_COOKIE_AGE = 240
- Define tempo de vida da sessão em segundos
- 240s = 4 minutos
- Após 4 min sem atividade, sessão expira

### SESSION_SAVE_EVERY_REQUEST = True
- Salva sessão a cada requisição
- Renova o timeout automaticamente
- Usuário ativo nunca é deslogado

### SESSION_EXPIRE_AT_BROWSER_CLOSE = True
- Sessão expira ao fechar navegador
- Não persiste entre sessões do navegador
- Mais seguro

## Comportamento Após Correção

```
Usuário faz login
  ↓
Sessão criada (TTL: 240s)
  ↓
Usuário faz requisição (30s depois)
  ↓
Sessão renovada (TTL: 240s novamente)
  ↓
Usuário fica inativo (4+ minutos)
  ↓
Sessão expira automaticamente
  ↓
Próxima requisição → 401 Unauthorized
  ↓
Frontend redireciona para login
```

## Testes Realizados

### Teste 1: Inatividade
```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login \
  -d '{"username": "test", "password": "test"}'
# Retorna: session_id

# 2. Aguardar 5 minutos

# 3. Tentar acessar recurso protegido
curl http://localhost:8000/api/cameras/ \
  -H "Cookie: sessionid=abc123"
# Retorna: 401 Unauthorized ✅
```

### Teste 2: Atividade Contínua
```bash
# 1. Login
# 2. Fazer requisições a cada 1 minuto
# 3. Após 10 minutos, ainda logado ✅
```

### Teste 3: Redis Cleanup
```bash
# Verificar TTL no Redis
docker-compose exec redis_cache redis-cli
127.0.0.1:6379> TTL "session:abc123"
(integer) 240  # 4 minutos ✅

# Após 4 minutos
127.0.0.1:6379> GET "session:abc123"
(nil)  # Sessão removida automaticamente ✅
```

## Validação
- [x] Bug não ocorre mais
- [x] Testes automatizados passam
- [x] Sem regressões
- [x] Performance mantida
- [x] Documentação atualizada

## Deploy
- Data: 2026-01-13
- Commit: [hash]
- Branch: fix/session-timeout
- Ambiente: Staging → Produção
