from django.db import models
from django.utils import timezone

class ConfiguracaoGlobal(models.Model):
    """Modelo Singleton para configurações globais."""
    notificacoes_habilitadas = models.BooleanField(default=True)
    email_suporte = models.EmailField(max_length=255, blank=True, null=True)
    em_manutencao = models.BooleanField(default=False)

    # Corrigido para evitar IntegrityError em SQLite durante testes
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(ConfiguracaoGlobal, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @staticmethod
    def load():
        obj, _ = ConfiguracaoGlobal.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = "Configuração Global"
        verbose_name_plural = "Configurações Globais"