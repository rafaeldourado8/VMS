# Commit - PASSO 2

```bash
git add src/shared/admin/cameras/
git add src/config/settings.py
git add docs/passo2-camera/

git commit -m "feat: domínio Camera com isolamento multi-tenant

PASSO 2 - Domínio Camera:
- Model Camera (UUID duplo: id + public_id)
- FK para City (isolamento obrigatório)
- Enums: CameraProtocol, UserRole
- Permissões customizadas (view_city_cameras, manage_city_cameras)
- Grupos pré-configurados (GESTOR, USER)
- Admin interface completa
- 16 testes passando

Regras:
- public_id é a única identidade exposta
- id nunca sai do domínio
- city_id obrigatório em tudo
- Nome único por cidade
- Cascade delete com City

Permissões:
- SUPERADMIN: tudo (is_superuser)
- GESTOR: gerencia câmeras da cidade
- USER: visualiza streams da cidade

Testes: ✅ 16/16 passing

Refs: RULES.md PASSO 2"
```

## Validação

```bash
# Grupos criados
docker exec -it vms_django python manage.py shell -c "from django.contrib.auth.models import Group; print(list(Group.objects.values_list('name', flat=True)))"

# Permissões do GESTOR
docker exec -it vms_django python manage.py shell -c "from django.contrib.auth.models import Group; g=Group.objects.get(name='GESTOR'); print([p.codename for p in g.permissions.all()])"

# Câmeras no admin
curl -I http://localhost:8000/admin/cameras/camera/
```
