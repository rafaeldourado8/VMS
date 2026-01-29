from django.apps import AppConfig

class CamerasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cameras"
    verbose_name = "Gerenciamento de Câmeras"

    def ready(self):
        # Importa os signals para registrá-los quando o Django iniciar
        import apps.cameras.signals