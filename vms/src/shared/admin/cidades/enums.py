from django.db import models

class CityStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Ativo'
    INACTIVE = 'INACTIVE', 'Inativo'
    SUSPENDED = 'SUSPENDED', 'Suspenso'

class Plan(models.TextChoices):
    BASIC = 'BASIC', 'Básico'
    STANDARD = 'STANDARD', 'Padrão'
    PREMIUM = 'PREMIUM', 'Premium'
