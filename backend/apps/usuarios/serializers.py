from rest_framework import serializers

from .models import Usuario  # Importa o modelo que já criamos


class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Usuario

        # Estes são os campos que sua API vai expor
        # (Exatamente como na sua documentação, Endpoint 7.1)
        fields = ["id", "email", "name", "role", "is_active", "created_at", "password"]

        # Campos que são apenas para leitura (não podem ser definidos na criação)
        read_only_fields = ["id", "created_at"]

    # Este método é chamado quando um POST /api/users/ é feito (Endpoint 7.2)
    # Precisamos dele para criptografar a senha corretamente.
    def create(self, validated_data):
        password = validated_data.pop("password", None)

        # Cria o usuário, mas ainda não tem senha
        instance = self.Meta.model(**validated_data)

        if password:
            instance.set_password(password)  # Criptografa a senha

        instance.save()
        return instance
