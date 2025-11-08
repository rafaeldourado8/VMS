from django.db import models


class ConfiguracaoGlobal(models.Model):
    """
    Modelo Singleton para armazenar configurações globais do sistema.
    Haverá apenas um registro deste modelo no banco (pk=1).
    """

    # --- Campos de Exemplo (Seção 8 da documentação) ---

    # Ex: Notificações
    notificacoes_habilitadas = models.BooleanField(
        default=True, help_text="Habilita/desabilita todas as notificações do sistema."
    )
    email_suporte = models.EmailField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Email para onde as solicitações de suporte são enviadas.",
    )

    # Ex: Manutenção
    em_manutencao = models.BooleanField(
        default=False, help_text="Coloca o sistema em modo de manutenção."
    )

    # --- Campos de Controle ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Configurações Globais do Sistema"

    def save(self, *args, **kwargs):
        """
        Garante que apenas uma instância seja salva, forçando o ID (pk) para 1.
        """
        self.pk = 1
        super(ConfiguracaoGlobal, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Impede a exclusão deste objeto.
        """
        pass  # Não faz nada

    @staticmethod
    def load():
        """
        Carrega (ou cria) a instância única de configurações.
        Este é o método que usaremos nas Views.
        """
        obj, created = ConfiguracaoGlobal.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = "Configuração Global"
        verbose_name_plural = "Configurações Globais"
