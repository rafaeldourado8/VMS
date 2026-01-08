from infrastructure.persistence.django.repositories.django_support_repository import DjangoSupportRepository
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from application.support.commands.create_support_message_command import CreateSupportMessageCommand
from application.support.handlers.create_support_message_handler import CreateSupportMessageHandler

class SupportMessageAPIView(APIView):
    """API para mensagens de suporte usando DDD"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self):
        super().__init__()
        self._repository = DjangoSupportRepository()
        self._create_handler = CreateSupportMessageHandler(self._repository)
    
    def get(self, request):
        """Lista mensagens do usuário"""
        messages = self._repository.get_messages_by_user(request.user.id)
        
        data = [
            {
                "id": msg.id,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "is_admin_response": msg.is_admin_response
            }
            for msg in messages
        ]
        
        return Response(data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Cria nova mensagem de suporte"""
        content = request.data.get('content', '').strip()
        
        if not content:
            return Response(
                {"error": "Conteúdo é obrigatório"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        command = CreateSupportMessageCommand(
            author_id=request.user.id,
            content=content,
            is_admin_response=request.user.is_staff
        )
        
        try:
            message = self._create_handler.handle(command)
            return Response(
                {
                    "id": message.id,
                    "content": message.content,
                    "timestamp": message.timestamp,
                    "is_admin_response": message.is_admin_response
                },
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )