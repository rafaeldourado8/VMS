from rest_framework import serializers
from .models import ConfiguracaoGlobal

class ConfiguracaoGlobalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoGlobal
        
        # Expõe todos os campos que definimos no modelo
        fields = [
            'notificacoes_habilitadas',
            'email_suporte',
            'em_manutencao',
            'updated_at'
        ]
        
        # Apenas para leitura
        read_only_fields = ['updated_at']