# Como Implementar Rate Limiting

## Problema

Sem rate limiting, APIs são vulneráveis a ataques de força bruta e DDoS.

## Soluções

### 1. Django Rate Limit

```bash
pip install django-ratelimit
```

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h', method='POST')
def login_view(request):
    pass

@ratelimit(key='user', rate='1000/d')
def api_view(request):
    pass
```

### 2. Django REST Framework Throttling

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

### 3. HAProxy Rate Limiting

```haproxy
frontend http-in
    stick-table type ip size 100k expire 30s store http_req_rate(10s)
    http-request track-sc0 src
    http-request deny if { sc_http_req_rate(0) gt 100 }
```

### 4. Nginx Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://backend;
}
```

## Checklist

- [ ] Rate limiting em login
- [ ] Rate limiting em APIs públicas
- [ ] Rate limiting em upload de arquivos
- [ ] Monitorar rate limit hits
- [ ] Ajustar limites conforme uso
