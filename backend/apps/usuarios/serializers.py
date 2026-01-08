from .models import Usuario

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer principal para operações CRUD."""
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Usuario
        fields = ["id", "email", "name", "role", "is_active", "created_at", "password"]
        read_only_fields = ["id", "created_at"]

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Customiza a resposta do login para incluir dados do utilizador."""
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UsuarioSerializer(self.user)
        data['user'] = serializer.data
        return data