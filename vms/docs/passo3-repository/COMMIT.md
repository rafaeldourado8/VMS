# Commit - PASSO 3

```bash
git add src/infrastructure/repositories/
git add docs/passo3-repository/

git commit -m "feat: repositories com isolamento multi-tenant obrigatório

PASSO 3 - Repository (contratos):
- Interface CityRepository
- Interface CameraRepository (city_id obrigatório)
- DjangoCityRepository (implementação ORM)
- DjangoCameraRepository (implementação ORM)
- 14 testes de isolamento

Regras:
- NUNCA buscar câmera sem city_id
- Todo acesso passa por interface
- ORM escondido atrás de abstrações
- Segurança por design

Padrões:
- SOLID (DIP)
- Clean Architecture
- DDD tático
- Anti-corruption layer

Testes: ✅ 14/14 passing

Refs: RULES.md PASSO 3"
```

## Validação

```bash
# Testes de isolamento
docker exec -it vms_django python manage.py test infrastructure.repositories.tests

# Verificar que city_id é obrigatório
docker exec -it vms_django python manage.py shell
>>> from infrastructure.repositories import DjangoCameraRepository
>>> repo = DjangoCameraRepository()
>>> repo.get_by_id  # Verificar assinatura
```
