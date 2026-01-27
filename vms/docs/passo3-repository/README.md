# PASSO 3 - Repository (Contratos)

## Objetivo

Criar contratos de acesso que:
- Escondem o ORM
- Forçam isolamento por tenant
- Impedem import direto de models
- Deixam domínio independente de Django

## Interfaces

### CityRepository

```python
get_by_id(city_id: UUID)
get_by_name(name: str)
list_active() -> List
exists(city_id: UUID) -> bool
```

### CameraRepository

```python
get_by_id(camera_id: UUID, city_id: UUID)          # city_id OBRIGATÓRIO
get_by_public_id(public_id: UUID, city_id: UUID)   # city_id OBRIGATÓRIO
list_by_city(city_id: UUID, is_active: bool) -> List
exists(camera_id: UUID, city_id: UUID) -> bool
count_by_city(city_id: UUID) -> int
```

## Implementações

- `DjangoCityRepository`: Implementação Django ORM
- `DjangoCameraRepository`: Implementação Django ORM

## Regras

**NUNCA buscar câmera sem city_id**

```python
# ❌ ERRADO
Camera.objects.get(id=camera_id)

# ✅ CORRETO
repo.get_by_id(camera_id, city_id)
```

## Segurança embutida

- Isolamento automático
- Zero vazamento cross-tenant
- Segurança por design

## Testes

✅ 14 testes passando

```bash
docker exec -it vms_django python manage.py test infrastructure.repositories.tests
```

## Uso

```python
from infrastructure.repositories import DjangoCameraRepository

repo = DjangoCameraRepository()
camera = repo.get_by_public_id(public_id, city_id)
```

## Próximo passo

**PASSO 4**: Middleware Tenant (extrai city_id do token)
