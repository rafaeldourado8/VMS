from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .serializers import MensagemSerializer
from .services import SuporteService
from .schemas import CreateMensagemDTO

class MensagemViewSet(viewsets.ModelViewSet):
    """ViewSet refatorada para usar SuporteService."""
    serializer_class = MensagemSerializer
    permission_classes = [permissions.IsAuthenticated]
    service = SuporteService()

    def get_queryset(self):
        return self.service.list_messages(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        dto = CreateMensagemDTO(conteudo=serializer.validated_data["conteudo"])
        mensagem = self.service.create_message(request.user, dto)
        
        output_serializer = self.get_serializer(mensagem)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)