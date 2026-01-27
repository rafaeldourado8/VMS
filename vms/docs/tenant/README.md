# PASSO 1 - Domínio Tenant (City)

## Objetivo

Criar a entidade base de isolamento multi-tenant: **City**.

## Model: City

```python
id = UUIDField(primary_key=True)
name = CharField(unique=True)
status = CharField(choices=CityStatus)
plan = CharField(choices=Plan)
created_at = DateTimeField(auto_now_add=True)
updated_at = DateTimeField(auto_now=True)
```

## Enums

**CityStatus**: ACTIVE, INACTIVE, SUSPENDED  
**Plan**: BASIC, STANDARD, PREMIUM

## Testes

✅ 7 testes passando

```bash
docker exec -it vms_django python manage.py test
```

## Admin

http://localhost:8000/admin

## Próximo passo

**PASSO 2**: Domínio Camera com `city_id` FK
