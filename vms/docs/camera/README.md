# PASSO 2 - Domínio Camera

## Objetivo

Criar entidade Camera com isolamento por `city_id` e `public_id` para exposição externa.

## Model: Camera

```python
id = UUIDField(primary_key=True)           # Interno, nunca exposto
public_id = UUIDField(unique=True)         # Exposto em URLs/APIs
city = ForeignKey(City, CASCADE)           # Isolamento multi-tenant
name = CharField(max_length=255)
stream_url = CharField(max_length=512)
protocol = CharField(choices=CameraProtocol)
is_lpr = BooleanField(default=False)
is_active = BooleanField(default=True)
```

## Regras

- **UUID duplo**: `id` interno, `public_id` exposto
- **Isolamento**: `city_id` obrigatório
- **Nome único por cidade**: `unique_together=['city', 'name']`
- **Cascade delete**: Deletar cidade → deletar câmeras

## Permissões

### Grupos criados

- **GESTOR**: Gerencia câmeras da própria cidade
- **USER**: Visualiza streams da própria cidade
- **SUPERADMIN**: `is_superuser=True` (tudo)

### Permissões customizadas

- `cameras.view_city_cameras` → USER
- `cameras.manage_city_cameras` → GESTOR

## Setup

```bash
docker exec -it vms_django python manage.py setup_groups
```

## Testes

✅ 16 testes passando

```bash
docker exec -it vms_django python manage.py test
```

## Admin

http://localhost:8000/admin/cameras/camera/

## Próximo passo

**PASSO 3**: Repository (contratos de acesso com city_id obrigatório)
