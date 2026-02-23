#!/bin/bash

# Configurar seu Instance ID aqui
INSTANCE_ID="i-XXXXXXXXX"  # SUBSTITUIR PELO SEU ID

if [ "$INSTANCE_ID" = "i-XXXXXXXXX" ]; then
    echo "❌ Erro: Configure o INSTANCE_ID no script primeiro!"
    echo ""
    echo "Para obter seu Instance ID:"
    echo "aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==\`Name\`].Value|[0],State.Name]' --output table"
    exit 1
fi

echo "🛑 Parando instância VMS Dev..."
echo "Instance ID: $INSTANCE_ID"
echo ""

aws ec2 stop-instances --instance-ids $INSTANCE_ID

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Comando enviado com sucesso!"
    echo ""
    echo "A instância está sendo desligada..."
    echo "Economia: ~\$0.03/hora (~\$0.72/dia)"
    echo ""
    echo "Para ligar novamente: bash scripts/aws/start-dev.sh"
else
    echo ""
    echo "❌ Erro ao parar instância"
    echo "Verifique suas credenciais AWS e o Instance ID"
fi
