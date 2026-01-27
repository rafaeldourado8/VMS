# Testes - PASSO 1: Domínio Tenant (City)

## Executar testes

```bash
docker exec -it vms_django python manage.py test
```

### Apenas City model

```bash
docker exec -it vms_django python manage.py test shared.admin.cidades.tests
```

### Apenas City admin

```bash
docker exec -it vms_django python manage.py test infrastructure.test.passo1-tenant
```

## Cobertura

### CityModelTest
- ✅ Criação de cidade
- ✅ UUID como primary key
- ✅ Status padrão (ACTIVE)
- ✅ Plano padrão (BASIC)
- ✅ Método is_active()
- ✅ Nome único
- ✅ String representation

### CityAdminTest
- ✅ Listagem no admin
- ✅ Formulário de criação
- ✅ Criação via admin

## Validação manual

http://localhost:8000/admin

## Checklist PASSO 1

- [x] Model City
- [x] UUID primary key
- [x] Enums
- [x] Admin interface
- [x] Testes
- [x] Migrations
