from rest_framework import serializers
# --- 1. Importe o TokenObtainPairSerializer ---
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Usuario  # Importa o modelo que já criamos


class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Usuario
        fields = ["id", "email", "name", "role", "is_active", "created_at", "password"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# --- 2. Adicione este novo Serializer no final do ficheiro ---
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customiza a resposta do login para incluir os dados do utilizador.
    """
    def validate(self, attrs):
        # Obtém a resposta padrão ({"access": "...", "refresh": "..."})
        data = super().validate(attrs)

        # Adiciona os dados do utilizador à resposta
        serializer = UsuarioSerializer(self.user)
        data['user'] = serializer.data
        
        return data