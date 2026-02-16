# Setup IAM - Instruções

## 🚀 Instalação Rápida

### Windows
```bash
cd backend
scripts\setup_iam.bat
```

### Linux/Mac
```bash
cd backend
chmod +x scripts/setup_iam.sh
./scripts/setup_iam.sh
```

### Manual
```bash
cd backend

# 1. Aplicar migrations
python manage.py makemigrations iam
python manage.py migrate iam

# 2. Carregar permissões
python manage.py load_permissions

# 3. Criar admin (opcional)
python manage.py createsuperuser
```

## ✅ Verificação

1. Acesse Django Admin: http://localhost:8000/admin
2. Verifique se aparecem:
   - IAM Permissions
   - IAM Rules
   - User Permissions
   - Tenant Isolation

3. Acesse Frontend: http://localhost:3000/settings/iam
4. Teste criar usuário e atribuir permissões

## 🔐 Usuário Admin Padrão

Se executou o script automático:
- Email: `admin@vms.com`
- Senha: `admin123`

**⚠️ IMPORTANTE**: Altere a senha em produção!

## 📋 Permissões Criadas

- `cameras.view` - Visualizar Câmeras
- `cameras.create` - Criar Câmeras
- `cameras.edit` - Editar Câmeras
- `cameras.delete` - Deletar Câmeras
- `recordings.view` - Visualizar Gravações
- `recordings.download` - Baixar Gravações
- `recordings.delete` - Deletar Gravações
- `detections.view` - Visualizar Detecções
- `users.manage` - Gerenciar Usuários
- `settings.manage` - Gerenciar Configurações

## 🧪 Teste de Isolamento

```python
# Django shell
python manage.py shell

from apps.usuarios.models import Usuario
from apps.cameras.models import Camera

# Criar usuários
user1 = Usuario.objects.create_user('user1@test.com', 'User 1', 'pass123')
user2 = Usuario.objects.create_user('user2@test.com', 'User 2', 'pass123')

# User1 cria câmera
camera = Camera.objects.create(name='Cam 1', stream_url='rtsp://test', owner=user1)
camera.grant_access_to_user(user1, read=True, write=True, delete=True)

# User2 não vê a câmera
print(Camera.objects.for_user(user2, 'camera').count())  # 0

# Compartilhar com User2
camera.grant_access_to_user(user2, read=True, write=False, delete=False)

# User2 agora vê
print(Camera.objects.for_user(user2, 'camera').count())  # 1
print(camera.user_can_access(user2, 'write'))  # False
```

## 🔧 Troubleshooting

### Erro: "No module named 'apps.iam'"
```bash
# Verifique se adicionou ao settings.py:
INSTALLED_APPS = [
    ...
    'apps.iam',
]
```

### Erro: "relation does not exist"
```bash
# Rode as migrations:
python manage.py migrate iam
```

### Erro: "ArrayField requires PostgreSQL"
```bash
# Use PostgreSQL ou altere models.py:
# Troque ArrayField por JSONField
```

## 📚 Documentação Completa

Ver: `docs/IAM_BACKEND.md`
