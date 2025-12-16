# 🔐 Checklist de Segurança - Autenticação

## ✅ Endpoints Públicos (Sem Token)
- [ ] `POST /api/auth/login/` - Login
- [ ] `POST /api/auth/refresh/` - Refresh token
- [ ] `GET /api/health/` - Health check (se existir)

## 🔒 Endpoints Protegidos (Requerem Token)
- [ ] `GET /api/auth/me/` - Dados do usuário
- [ ] `POST /api/auth/logout/` - Logout
- [ ] `GET /api/cameras/` - Listar câmeras
- [ ] `POST /api/cameras/` - Criar câmera
- [ ] `GET /api/deteccoes/` - Listar detecções
- [ ] `GET /api/analytics/*` - Analytics
- [ ] `GET /api/dashboard/*` - Dashboard

## 🔑 Endpoints com API Key (Ingestão Interna)
- [ ] `POST /api/deteccoes/ingest/` - Ingestão de detecções
  - Header: `X-API-Key: {INGEST_API_KEY}`

## 🚫 Erros Comuns a Evitar

### ❌ ERRO 1: IsAuthenticated Global
```python
# NUNCA faça isso:
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",  # Bloqueia login!
    ],
}
```

### ❌ ERRO 2: Kong JWT Plugin em /api/auth/*
```yaml
# NUNCA aplique JWT plugin na rota de autenticação:
routes:
  - name: auth-route
    paths: [/api/auth]
    plugins:
      - name: jwt  # ❌ Bloqueia login!
```

### ❌ ERRO 3: Esquecer AllowAny em Views Públicas
```python
# Se DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]:
class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]  # ✅ Obrigatório!
```

## 🧪 Testes Automatizados

### Teste 1: Login Público
```bash
curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
# Esperado: 200 OK + {access, refresh}
```

### Teste 2: Endpoint Protegido Sem Token
```bash
curl -X GET http://localhost/api/cameras/
# Esperado: 401 Unauthorized
```

### Teste 3: Endpoint Protegido Com Token
```bash
TOKEN="seu_token_aqui"
curl -X GET http://localhost/api/cameras/ \
  -H "Authorization: Bearer $TOKEN"
# Esperado: 200 OK + dados
```

## 📝 Configuração Atual

### Django (settings.py)
```python
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # ✅ Correto
    ],
}
```

### Kong (kong.yml)
```yaml
services:
  - name: django-api
    routes:
      - paths: [/api]
    plugins:
      - name: cors        # ✅ OK
      - name: rate-limiting  # ✅ OK
      # ✅ SEM plugin JWT/OAuth2
```

### Views Críticas
```python
# ✅ Público
class MyTokenObtainPairView(TokenObtainPairView):
    pass  # Herda AllowAny

# ✅ Protegido
class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

class CameraViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
```

## 🔄 Fluxo de Autenticação Correto

```
1. Cliente → POST /api/auth/login/ (SEM token)
   ↓
2. Django valida credenciais
   ↓
3. Django retorna {access, refresh}
   ↓
4. Cliente armazena tokens
   ↓
5. Cliente → GET /api/cameras/ (COM token)
   ↓
6. Django valida JWT
   ↓
7. Django retorna dados
```

## 🚀 Deploy em Produção

### Variáveis de Ambiente Críticas
```bash
# Django
SECRET_KEY=<50+ caracteres aleatórios>
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com

# JWT
SIMPLE_JWT_ACCESS_TOKEN_LIFETIME=5  # minutos
SIMPLE_JWT_REFRESH_TOKEN_LIFETIME=7  # dias

# API Key Interna
INGEST_API_KEY=<chave-forte-aleatória>
```

### Rate Limiting (Kong)
```yaml
plugins:
  - name: rate-limiting
    config:
      minute: 100      # Login: 100 req/min
      hour: 10000
```

### HTTPS Obrigatório
```python
# settings.py (produção)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

**✅ Última Verificação:** $(date)
**🔧 Responsável:** DevOps Team
