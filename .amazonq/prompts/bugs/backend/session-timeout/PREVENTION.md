# 🛡️ Prevenção - Session Timeout

## Medidas Preventivas Implementadas

### 1. Testes Automatizados

```python
# backend/apps/usuarios/tests/test_session_timeout.py

import time
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()

class SessionTimeoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_session_expires_after_inactivity(self):
        """Sessão deve expirar após 4 minutos de inatividade"""
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Verificar que está logado
        response = self.client.get('/api/cameras/')
        self.assertEqual(response.status_code, 200)
        
        # Simular 5 minutos de inatividade
        # (em teste, modificar SESSION_COOKIE_AGE temporariamente)
        with self.settings(SESSION_COOKIE_AGE=1):  # 1 segundo
            time.sleep(2)
            
            # Tentar acessar recurso protegido
            response = self.client.get('/api/cameras/')
            self.assertEqual(response.status_code, 401)
    
    def test_session_renews_with_activity(self):
        """Sessão deve renovar com atividade contínua"""
        self.client.login(username='testuser', password='testpass123')
        
        # Fazer requisições a cada 1 minuto por 10 minutos
        for _ in range(10):
            response = self.client.get('/api/cameras/')
            self.assertEqual(response.status_code, 200)
            time.sleep(60)  # 1 minuto
        
        # Ainda deve estar logado
        response = self.client.get('/api/cameras/')
        self.assertEqual(response.status_code, 200)
```

### 2. Validações Adicionadas

#### Settings Validation
```python
# backend/config/settings.py

# Validar configurações de sessão no startup
assert SESSION_COOKIE_AGE <= 300, "Session timeout deve ser <= 5 minutos"
assert SESSION_SAVE_EVERY_REQUEST is True, "Sessão deve renovar a cada request"
assert SESSION_EXPIRE_AT_BROWSER_CLOSE is True, "Sessão deve expirar ao fechar browser"
```

#### Middleware de Logging
```python
# backend/middleware/session_logging.py

import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class SessionLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            session_age = request.session.get_expiry_age()
            if session_age < 60:  # Menos de 1 minuto
                logger.warning(
                    f"Sessão próxima de expirar: {request.user.username} "
                    f"({session_age}s restantes)"
                )
```

### 3. Monitoramento

#### Prometheus Metrics
```python
# backend/metrics/session_metrics.py

from prometheus_client import Gauge, Counter

# Métricas
active_sessions = Gauge('active_sessions', 'Número de sessões ativas')
expired_sessions = Counter('expired_sessions_total', 'Total de sessões expiradas')
session_renewals = Counter('session_renewals_total', 'Total de renovações de sessão')

# Coletor
def collect_session_metrics():
    from django.contrib.sessions.models import Session
    active_count = Session.objects.filter(
        expire_date__gt=timezone.now()
    ).count()
    active_sessions.set(active_count)
```

#### Alertas
```yaml
# prometheus/alerts.yml

groups:
  - name: sessions
    rules:
      - alert: TooManySessions
        expr: active_sessions > 1000
        for: 5m
        annotations:
          summary: "Muitas sessões ativas"
          description: "{{ $value }} sessões ativas (limite: 1000)"
      
      - alert: SessionLeakSuspected
        expr: rate(active_sessions[1h]) > 100
        for: 10m
        annotations:
          summary: "Possível vazamento de sessões"
          description: "Crescimento anormal de sessões"
```

### 4. Documentação

#### README Atualizado
```markdown
## Configuração de Sessões

O sistema usa timeout de 4 minutos para sessões inativas:
- `SESSION_COOKIE_AGE = 240` (4 minutos)
- `SESSION_SAVE_EVERY_REQUEST = True` (renova automaticamente)
- `SESSION_EXPIRE_AT_BROWSER_CLOSE = True` (não persiste)

### Por que 4 minutos?
- Segurança: Reduz janela de ataque
- UX: Usuários ativos nunca são deslogados
- Recursos: Limpa sessões abandonadas rapidamente
```

#### Checklist de Configuração
```markdown
# .amazonq/prompts/checklists/django-security.md

## Django Security Checklist

### Sessões
- [ ] SESSION_COOKIE_AGE configurado (≤ 5 minutos)
- [ ] SESSION_SAVE_EVERY_REQUEST = True
- [ ] SESSION_EXPIRE_AT_BROWSER_CLOSE = True
- [ ] SESSION_COOKIE_HTTPONLY = True
- [ ] SESSION_COOKIE_SECURE = True (produção)
- [ ] SESSION_COOKIE_SAMESITE = 'Lax'
- [ ] Testes de timeout implementados
- [ ] Monitoramento configurado
```

---

## Lições Aprendidas

### O que funcionou bem
1. **Configuração simples:** Apenas 3 linhas resolveram o problema
2. **Sem breaking changes:** Usuários ativos não foram afetados
3. **Testes claros:** Fácil validar a correção

### O que pode melhorar
1. **Checklist inicial:** Deveria ter sido verificado no setup
2. **Testes de segurança:** Adicionar ao CI/CD
3. **Documentação:** Documentar decisões de configuração

---

## Checklist de Prevenção

Para evitar bugs similares no futuro:

### Desenvolvimento
- [x] Adicionar testes de edge cases (inatividade, atividade contínua)
- [x] Revisar código relacionado (autenticação, middleware)
- [x] Atualizar documentação (README, settings)
- [x] Criar checklist de segurança

### Operacional
- [x] Adicionar monitoramento (Prometheus)
- [x] Configurar alertas (sessões anormais)
- [x] Revisar processo de QA (incluir testes de segurança)
- [x] Treinar equipe (compartilhar lições aprendidas)

### Arquitetura
- [ ] Considerar session store distribuído (futuro)
- [ ] Avaliar JWT como alternativa (futuro)
- [ ] Implementar refresh tokens (futuro)

---

## Aplicação em Outros Projetos

### Quando aplicar esta solução:
- ✅ Aplicações web com autenticação
- ✅ Sistemas com requisitos de segurança
- ✅ Aplicações com múltiplos usuários simultâneos
- ✅ Sistemas que precisam economizar recursos

### Quando NÃO aplicar:
- ❌ APIs stateless (usar JWT)
- ❌ Aplicações single-user
- ❌ Sistemas onde usuário deve permanecer logado indefinidamente
