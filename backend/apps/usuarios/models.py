# apps/usuarios/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# Este é o "Manager" - ele ensina o Django a criar usuários
class UsuarioManager(BaseUserManager):
    
    # Método para criar um usuário comum
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password) # Criptografa a senha
        user.save(using=self._db)
        return user

    # Método para criar um superusuário (admin)
    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin') # Definindo a role padrão para admin

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário deve ter is_superuser=True.')

        return self.create_user(email, name, password, **extra_fields)

# Este é o Modelo de Usuário principal
class Usuario(AbstractBaseUser, PermissionsMixin):
    
    # Estas são as "Funções" da sua API (Endpoint 7.1)
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('viewer', 'Visualizador'),
        # Adicione outros papéis se precisar
    )

    # Campos do seu banco de dados
    # Isso bate com a API (Endpoint 7.1)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='viewer')
    
    # Estes campos são exigidos pelo Django para o Admin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) # 'is_staff' controla o acesso ao Admin do Django
    
    # Campo 'created_at' da sua API (Endpoint 7.1)
    created_at = models.DateTimeField(default=timezone.now) 

    # Diz ao Django para usar nosso Manager personalizado
    objects = UsuarioManager()

    # Diz ao Django que o campo 'email' será usado para login
    USERNAME_FIELD = 'email'
    
    # Campos obrigatórios ao criar um usuário (além de email e senha)
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email