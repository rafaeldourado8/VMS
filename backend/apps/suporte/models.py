from django.conf import settings
from django.db import models

class Mensagem(models.Model):
    """
    Modelo para armazenar mensagens de suporte (Seção 6).
    """

    # Relacionamento: Quem enviou a mensagem?
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # Se o usuário for deletado, suas mensagens somem
        related_name="mensagens_suporte",
    )

    # Conteúdo da mensagem
    conteudo = models.TextField()

    # Controle de data
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Campo para o frontend saber se é uma resposta do admin
    respondido_por_admin = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"Mensagem de {self.autor.email} em {self.timestamp.strftime('%Y-%m-%d')}"
        )

    class Meta:
        ordering = ["-timestamp"]  # Mostrar as mais novas primeiro
        verbose_name = "Mensagem de Suporte"
        verbose_name_plural = "Mensagens de Suporte"
