# PASSO 4 - Middleware Tenant

## Objetivo

Extrair, validar e injetar `city_id` em toda requisição.

## Funcionamento

1. ✅ **Resolve tenant**: Extrai `X-City-ID` do header
2. ✅ **Valida tenant**: Verifica UUID e existência
3. ✅ **Injeta contexto**: `request.city_id`
4. ✅ **Bloqueia sem tenant**: 400 se header ausente
5. ✅ **Bloqueia mismatch**: 404 se cidade não existe
6. ✅ **Ignora rotas públicas**: `/admin/`, `/static/`, `/health/`
7. ✅ **Loga tenant**: INFO com city_id e path

## Uso

```python
# Cliente envia
X-City-ID: c21a0980-4281-4f59-b164-ff07d4c27f43

# View recebe
def my_view(request):
    city_id = request.city_id  # UUID já validado
```

## Bypass

- **Superadmin**: `is_superuser=True` bypassa validação
- **Rotas públicas**: `/admin/`, `/static/`, `/health/`

## Logs

```
INFO Tenant resolved: c21a0980-4281-4f59-b164-ff07d4c27f43 | Path: /api/cameras/
WARNING Missing X-City-ID header: /api/cameras/
WARNING Invalid X-City-ID format: invalid-uuid
WARNING City not found: 1997f5ee-9b40-47a1-af3f-b5bec869aaec
```

## Testes

✅ 8 testes passando

```bash
docker exec -it vms_django python manage.py test infrastructure.middleware.tests
```

## Próximo passo

**PASSO 5**: StreamingManager (core do produto)
