# 🔍 Análise de Causa Raiz - Session Timeout

## Investigação

### Hipóteses Iniciais
1. Django não configurado para expirar sessões
2. Redis não está limpando chaves antigas
3. Frontend não está detectando sessão expirada
4. Middleware de sessão não está ativo

### Testes Realizados
- [x] Teste 1: Verificar `settings.py` → **Sem configuração de timeout**
- [x] Teste 2: Verificar Redis TTL → **TTL não configurado**
- [x] Teste 3: Verificar middleware → **Middleware ativo, mas sem timeout**

## Causa Raiz Identificada

### Problema Principal
Django não está configurado com `SESSION_COOKIE_AGE` e `SESSION_SAVE_EVERY_REQUEST` adequados.

### Por que aconteceu?

**Configuração padrão do Django:**
```python
# settings.py (ANTES)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
# SESSION_COOKIE_AGE não definido (padrão: 2 semanas)
# SESSION_SAVE_EVERY_REQUEST não definido (padrão: False)
```

**Comportamento padrão:**
- `SESSION_COOKIE_AGE = 1209600` (2 semanas)
- `SESSION_SAVE_EVERY_REQUEST = False` (só salva quando modificada)
- Resultado: Sessão dura 2 semanas sem expirar

### Código Problemático

```python
# backend/config/settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
# ❌ Faltando configurações de timeout
```

### Por que não foi detectado antes?

1. **Configuração padrão aceita:** Django funciona "normalmente" com padrões
2. **Sem testes de inatividade:** Não testamos cenário de usuário inativo
3. **Foco em funcionalidade:** Priorizamos features sobre segurança/recursos
4. **Sem monitoramento de sessões:** Não monitoramos crescimento de sessões no Redis

## Análise dos 5 Porquês

1. **Por quê sessões não expiram?**
   - Porque não há timeout configurado

2. **Por quê não há timeout configurado?**
   - Porque usamos configuração padrão do Django

3. **Por quê usamos configuração padrão?**
   - Porque não revisamos requisitos de segurança/recursos

4. **Por quê não revisamos requisitos?**
   - Porque focamos em MVP rápido sem checklist de segurança

5. **Por quê não tínhamos checklist?**
   - Porque não documentamos best practices de configuração

**Causa Raiz:** Falta de checklist de segurança e recursos na configuração inicial.

## Fatores Contribuintes

1. **Documentação Django:** Padrão de 2 semanas não é óbvio
2. **Priorização:** Features antes de otimizações
3. **Testes:** Sem testes de cenários de inatividade
4. **Monitoramento:** Sem alertas de crescimento de sessões
