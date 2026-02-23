#!/bin/bash

echo "=== Criando EC2 Spot Instance para VMS ==="
echo ""

# Verificar AWS CLI
if ! command -v aws &> /dev/null; then
    echo "Erro: AWS CLI não instalado"
    echo "Instale: https://aws.amazon.com/cli/"
    exit 1
fi

# Configurações
REGION="us-east-1"
SPOT_PRICE="0.10"
KEY_NAME="vms-dev-key"
SG_NAME="vms-dev-sg"

# Criar Security Group
echo "1. Criando Security Group..."
SG_ID=$(aws ec2 create-security-group \
    --group-name $SG_NAME \
    --description "VMS Development Server" \
    --region $REGION \
    --output text --query 'GroupId' 2>/dev/null)

if [ -z "$SG_ID" ]; then
    echo "Security Group já existe ou erro ao criar"
    SG_ID=$(aws ec2 describe-security-groups \
        --group-names $SG_NAME \
        --region $REGION \
        --output text --query 'SecurityGroups[0].GroupId')
fi

echo "Security Group ID: $SG_ID"

# Adicionar regras
echo "2. Configurando regras de firewall..."
aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --ip-permissions \
        IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges='[{CidrIp=0.0.0.0/0,Description="SSH"}]' \
        IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges='[{CidrIp=0.0.0.0/0,Description="HTTP"}]' \
        IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges='[{CidrIp=0.0.0.0/0,Description="HTTPS"}]' \
        IpProtocol=tcp,FromPort=8554,ToPort=8554,IpRanges='[{CidrIp=0.0.0.0/0,Description="RTSP"}]' \
        IpProtocol=tcp,FromPort=8404,ToPort=8404,IpRanges='[{CidrIp=0.0.0.0/0,Description="HAProxy Stats"}]' \
    --region $REGION 2>/dev/null

# Criar Spot Instance
echo "3. Criando Spot Instance Request..."
REQUEST_ID=$(aws ec2 request-spot-instances \
    --spot-price $SPOT_PRICE \
    --instance-count 1 \
    --type "one-time" \
    --launch-specification file://spot-instance-config.json \
    --region $REGION \
    --output text --query 'SpotInstanceRequests[0].SpotInstanceRequestId')

echo "Spot Request ID: $REQUEST_ID"

# Aguardar instância
echo "4. Aguardando instância ser criada..."
sleep 10

INSTANCE_ID=$(aws ec2 describe-spot-instance-requests \
    --spot-instance-request-ids $REQUEST_ID \
    --region $REGION \
    --output text --query 'SpotInstanceRequests[0].InstanceId')

echo "Instance ID: $INSTANCE_ID"

# Aguardar instância estar running
echo "5. Aguardando instância iniciar..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

# Obter IP público
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --output text --query 'Reservations[0].Instances[0].PublicIpAddress')

echo ""
echo "=== Instância criada com sucesso! ==="
echo ""
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo ""
echo "Conectar via SSH:"
echo "ssh -i $KEY_NAME.pem ubuntu@$PUBLIC_IP"
echo ""
echo "Aguarde 2-3 minutos para o setup inicial completar"
