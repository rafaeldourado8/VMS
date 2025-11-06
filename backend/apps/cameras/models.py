# apps/cameras/models.py

from django.conf import settings  # Para pegar o modelo de usuário (AUTH_USER_MODEL)
from django.db import models

# Isso vem da sua documentação (ex: "status": "online")
STATUS_CHOICES = (("online", "Online"), ("offline", "Offline"))


class Camera(models.Model):
    # O "dono" da câmera. Se o usuário for deletado, suas câmeras também serão.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cameras",  # Permite fazer user.cameras.all()
    )

    # --- Campos da sua API (Seção 3.1) ---
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="offline")

    # Usamos max_length=1000 para URLs longas de stream
    stream_url = models.CharField(max_length=1000)

    # O campo 'thumbnail' da sua API
    thumbnail_url = models.CharField(max_length=1000, blank=True, null=True)

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    # --- Campo da sua API (Seção 3.2) ---
    # JSONField é perfeito para guardar configurações como {'enabled': true, ...}
    detection_settings = models.JSONField(default=dict, blank=True, null=True)

    # --- Campos de controle (boa prática) ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
