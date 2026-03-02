# Riscos de Deployment

## 🔴 Crítico

### 1. DEBUG=True em Produção
**Impacto:** Exposição de stack traces, informações sensíveis

**Ação Requerida:**
```python
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
SECRET_KEY = os.getenv('SECRET_KEY')
```

### 2. Logs com Informações Sensíveis
**Ação Requerida:**
- Não logar senhas, tokens, PII
- Usar log levels adequados
- Implementar log rotation

### 3. Falta de Rate Limiting
**Ação Requerida:**
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h')
def api_view(request):
    pass
```

## 🟠 Alto

### 4. Backup Strategy Inadequada
**Ação Requerida:**
- Backup automático diário
- Retenção de 30 dias
- Testes de restore mensais

### 5. Monitoring Insuficiente
**Ação Requerida:**
- Implementar Prometheus + Grafana
- Alertas para erros críticos
- Dashboards de performance

## 📋 Checklist

- [ ] DEBUG=False em produção
- [ ] SECRET_KEY único e seguro
- [ ] ALLOWED_HOSTS configurado
- [ ] Rate limiting implementado
- [ ] Logs sem PII
- [ ] Backup automatizado
- [ ] Monitoring configurado
- [ ] Alertas configurados
