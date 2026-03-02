# Como Configurar CORS Seguro

## Problema

CORS mal configurado permite acesso de origens maliciosas.

## Configuração Insegura

```python
# ❌ INSEGURO
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
```

## Configuração Segura

### 1. Whitelist de Origens
```python
# ✅ SEGURO
CORS_ALLOWED_ORIGINS = [
    "https://vms.example.com",
    "https://app.example.com",
]

# Para desenvolvimento
if DEBUG:
    CORS_ALLOWED_ORIGINS += ["http://localhost:3000"]
```

### 2. Métodos Permitidos
```python
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'DELETE',
]
```

### 3. Headers Permitidos
```python
CORS_ALLOW_HEADERS = [
    'accept',
    'authorization',
    'content-type',
]
```

### 4. Credentials
```python
# Apenas se necessário
CORS_ALLOW_CREDENTIALS = True
```

## Nginx CORS

```nginx
location /api/ {
    if ($request_method = 'OPTIONS') {
        add_header 'Access-Control-Allow-Origin' 'https://vms.example.com';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type';
        return 204;
    }
    
    add_header 'Access-Control-Allow-Origin' 'https://vms.example.com' always;
    proxy_pass http://backend;
}
```

## Checklist

- [ ] Remover CORS_ALLOW_ALL_ORIGINS
- [ ] Configurar whitelist de origens
- [ ] Limitar métodos HTTP
- [ ] Limitar headers
- [ ] Testar em produção
