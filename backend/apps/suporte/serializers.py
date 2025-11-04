from rest_framework import serializers
from .models import Mensagem

class MensagemSerializer(serializers.ModelSerializer):
    # Vamos mostrar o email do autor, é mais útil
    autor_email = serializers.EmailField(source='autor.email', read_only=True)
    autor_id = serializers.IntegerField(source='autor.id', read_only=True)

    class Meta:
        model = Mensagem
        
        # Campos que a API vai expor (Seção 6.1 e 6.2)
        fields = [
            'id', 
            'autor_id',
            'autor_email', 
            'conteudo', 
            'timestamp', 
            'respondido_por_admin'
        ]
        
        # O usuário só pode enviar o 'conteudo'.
        # O resto é definido automaticamente pelo backend.
        read_only_fields = [
            'id', 
            'autor_id', 
            'autor_email', 
            'timestamp', 
            'respondido_por_admin'
        ]