from django.db import models

# Baseado na sua API (Seção 5.3)
VEHICLE_TYPE_CHOICES = (
    ("car", "Carro"),
    ("motorcycle", "Motocicleta"),
    ("truck", "Caminhão"),
    ("bus", "Ônibus"),
    ("unknown", "Desconhecido"),
)


class Deteccao(models.Model):
    # RELACIONAMENTO: A qual câmera esta detecção pertence?
    # Isso cria o 'camera_id' que sua API pede.
    camera = models.ForeignKey(
        "cameras.Camera",  # Aponta para o app 'cameras', modelo 'Camera'
        on_delete=models.CASCADE,  # Se a câmera for deletada, as detecções vão junto
        related_name="deteccoes",  # Permite fazer camera.deteccoes.all()
    )

    # --- Campos da API (Seção 4.1) ---

    # 'plate': 'ABC-1234'. Indexado para buscas rápidas
    plate = models.CharField(max_length=20, blank=True, null=True, db_index=True)

    # 'confidence': 0.95
    confidence = models.FloatField(blank=True, null=True)

    # 'timestamp': '2025-10-16T14:59:47Z'
    # Este campo é CRÍTICO para filtros. 'db_index=True' acelera as buscas.
    # Não usamos 'auto_now_add' porque o worker vai mandar o timestamp exato.
    timestamp = models.DateTimeField(db_index=True)

    # 'vehicle_type': 'car'
    vehicle_type = models.CharField(
        max_length=20, choices=VEHICLE_TYPE_CHOICES, default="unknown"
    )

    # 'image_url': 'https://...' (Usamos CharField pela flexibilidade)
    image_url = models.CharField(max_length=1000, blank=True, null=True)

    # 'video_url': 'https://...'
    video_url = models.CharField(max_length=1000, blank=True, null=True)

    # --- Campo de Controle Interno ---
    created_at = models.DateTimeField(auto_now_add=True)  # Quando o registro foi salvo

    class Meta:
        ordering = ["-timestamp"]  # Sempre mostrar as detecções mais novas primeiro
        verbose_name = "Detecção"
        verbose_name_plural = "Detecções"

        indexes = [models.Index(fields=["camera", "-timestamp"])]

    def __str__(self):
        plate_display = self.plate or "N/A"
        return f"Detecção ({plate_display}) em {self.camera.name}"
