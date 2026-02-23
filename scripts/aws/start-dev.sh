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

echo "🚀 Iniciando instância VMS Dev..."
echo "Instance ID: $INSTANCE_ID"
echo ""

aws ec2 start-instances --instance-ids $INSTANCE_ID

if [ $? -ne 0 ]; then
    echo "❌ Erro ao iniciar instância"
    exit 1
fi

echo "⏳ Aguardando instância iniciar..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

NEW_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo ""
echo "✅ Instância iniciada com sucesso!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Novo IP Público: $NEW_IP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 URLs:"
echo "   Frontend:     http://$NEW_IP/"
echo "   API:          http://$NEW_IP/api/"
echo "   Admin:        http://$NEW_IP/admin/"
echo "   HAProxy:      http://$NEW_IP:8404/stats"
echo ""
echo "🔑 Conectar via SSH:"
echo "   ssh -i vms-dev-key.pem ubuntu@$NEW_IP"
echo ""
echo "⏰ Aguarde 1-2 minutos para Docker iniciar todos os serviços"
echo ""
echo "⚠️  IMPORTANTE: Se o IP mudou, atualize:"
echo "   - GitHub Secrets: DEV_SERVER_IP"
echo "   - .env no servidor: DJANGO_ALLOWED_HOSTS"
echo ""
