#!/bin/bash

echo "================================"
echo "  Setup IAM no Docker"
echo "================================"
echo ""

# Aplicar migrations
echo "[1/3] Aplicando migrations IAM..."
docker-compose exec backend python manage.py makemigrations iam
docker-compose exec backend python manage.py migrate iam
echo ""

# Carregar permissões
echo "[2/3] Carregando permissões iniciais..."
docker-compose exec backend python manage.py load_permissions
echo ""

# Criar admin (opcional)
echo "[3/3] Criando usuário admin..."
docker-compose exec backend python manage.py shell -c "
from apps.usuarios.models import Usuario
if not Usuario.objects.filter(email='admin@vms.com').exists():
    Usuario.objects.create_superuser(email='admin@vms.com', name='Administrator', password='admin123')
    print('✓ Usuário admin criado: admin@vms.com / admin123')
else:
    print('  Admin já existe')
"
echo ""

echo "================================"
echo "  IAM configurado com sucesso!"
echo "================================"
echo ""
echo "Acesse:"
echo "  Frontend: http://localhost/settings/iam"
echo "  Admin: http://localhost/admin"
echo ""
echo "Login:"
echo "  Email: admin@vms.com"
echo "  Senha: admin123"
echo ""
