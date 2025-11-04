from rest_framework import viewsets, permissions
from .models import Mensagem
from .serializers import MensagemSerializer

class MensagemViewSet(viewsets.ModelViewSet):
    """
    API endpoint para chat de suporte (Seção 6).
    - Permite GET (Listar) e POST (Criar).
    - Admins veem todas as mensagens.
    - Viewers veem apenas suas próprias mensagens.
    """
    serializer_class = MensagemSerializer
    permission_classes = [permissions.IsAuthenticated] # Exige login

    def get_queryset(self):
        """
        Filtra as mensagens baseado na role do usuário.
        """
        user = self.request.user

        if user.role == 'admin':
            # Admin vê todas as mensagens de todos os usuários
            # Agrupadas por autor e data
            return Mensagem.objects.all().order_by('autor__email', '-timestamp')
        
        # Usuário 'viewer' vê apenas suas próprias mensagens
        return Mensagem.objects.filter(autor=user).order_by('-timestamp')

    def perform_create(self, serializer):
        """
        Define o 'autor' da mensagem automaticamente como o usuário logado.
        """
        
        # Se quem envia é admin, marcamos como "resposta"
        is_admin_response = self.request.user.role == 'admin'
        
        serializer.save(
            autor=self.request.user,
            respondido_por_admin=is_admin_response
        )