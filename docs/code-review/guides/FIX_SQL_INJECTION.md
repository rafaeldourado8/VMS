# Como Corrigir SQL Injection

## Problema

SQL Injection ocorre quando dados do usuário são concatenados diretamente em queries SQL.

## Exemplos Vulneráveis

```python
# ❌ VULNERÁVEL
camera_id = request.GET.get('id')
query = f"SELECT * FROM cameras WHERE id = {camera_id}"
cursor.execute(query)

# ❌ VULNERÁVEL
name = request.POST.get('name')
query = "SELECT * FROM cameras WHERE name = '" + name + "'"
cursor.execute(query)
```

## Correções

### 1. Usar Django ORM
```python
# ✅ SEGURO
camera_id = request.GET.get('id')
camera = Camera.objects.get(id=camera_id)
```

### 2. Usar Parameterized Queries
```python
# ✅ SEGURO
camera_id = request.GET.get('id')
query = "SELECT * FROM cameras WHERE id = %s"
cursor.execute(query, [camera_id])
```

### 3. Validar Inputs
```python
# ✅ SEGURO
from django.core.validators import validate_integer

camera_id = request.GET.get('id')
try:
    validate_integer(camera_id)
    camera = Camera.objects.get(id=camera_id)
except (ValueError, ValidationError):
    return HttpResponseBadRequest("Invalid ID")
```

## Checklist

- [ ] Nunca concatenar strings em queries
- [ ] Sempre usar parameterized queries
- [ ] Validar todos os inputs
- [ ] Usar Django ORM quando possível
- [ ] Testar com payloads maliciosos
