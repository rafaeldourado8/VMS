# 🔐 Credenciais de Login - GT-Vision

## ✅ Superusuário Criado

### Credenciais
```
Email: admin@gtvision.com
Senha: admin123
```

## Endpoints de Autenticação

### Login
```bash
POST http://localhost/api/auth/login/
Content-Type: application/json

{
  "email": "admin@gtvision.com",
  "password": "admin123"
}
```

### Resposta
```json
{
  "refresh": "eyJhbGci...",
  "access": "eyJhbGci...",
  "user": {
    "id": 3,
    "email": "admin@gtvision.com",
    "name": "Admin",
    "role": "admin",
    "is_active": true
  }
}
```

## Acesso Frontend

### URL
```
http://localhost
```

### Login
1. Acesse http://localhost
2. Email: `admin@gtvision.com`
3. Senha: `admin123`

## Acesso Admin Django

### URL
```
http://localhost/admin/
```

### Login
- Email: `admin@gtvision.com`
- Senha: `admin123`

## Criar Novos Usuários

### Via Django Shell
```bash
docker exec gtvision_backend python manage.py shell -c "
from apps.usuarios.models import Usuario;
Usuario.objects.create_user(
    email='usuario@exemplo.com',
    password='senha123',
    name='Nome Usuario',
    role='operator'
)
"
```

### Via API (como admin)
```bash
curl -X POST http://localhost/api/usuarios/ \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@exemplo.com",
    "password": "senha123",
    "name": "Nome Usuario",
    "role": "operator"
  }'
```

## Roles Disponíveis
- `admin` - Acesso total
- `operator` - Operador (visualização e controle)
- `viewer` - Apenas visualização

---

**Nota**: Altere a senha padrão em produção!
