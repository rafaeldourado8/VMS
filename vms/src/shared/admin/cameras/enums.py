from django.db import models

class CameraProtocol(models.TextChoices):
    RTSP = 'RTSP', 'RTSP'
    RTMP = 'RTMP', 'RTMP'

class UserRole(models.TextChoices):
    SUPERADMIN = 'SUPERADMIN', 'Superadmin'
    GESTOR = 'GESTOR', 'Gestor'
    USER = 'USER', 'Usuário'
