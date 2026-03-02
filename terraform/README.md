# Terraform VMS - Guia de Deploy

## Pré-requisitos

✅ AWS CLI configurado (já feito)
✅ Terraform instalado
✅ S3 bucket criado: `vms-terraform-state-gtvision`
✅ ECR repositories criados

## 1. Criar Key Pair SSH

```bash
# Via AWS Console
AWS Console → EC2 → Key Pairs → Create key pair
Nome: vms-dev-key
Tipo: RSA
Formato: .pem

# Ou via CLI
aws ec2 create-key-pair --key-name vms-dev-key --query 'KeyMaterial' --output text > vms-dev-key.pem
chmod 400 vms-dev-key.pem
```

## 2. Deploy Desenvolvimento

```bash
cd terraform/dev

# Inicializar Terraform
terraform init

# Configurar variáveis
cp terraform.tfvars.example terraform.tfvars
# Edite terraform.tfvars com seu IP

# Planejar
terraform plan

# Aplicar
terraform apply

# Ver outputs
terraform output
```

## 3. Deploy Produção

```bash
cd terraform/prod

# Inicializar
terraform init

# Configurar variáveis
cp terraform.tfvars.example terraform.tfvars
# Edite terraform.tfvars com senha forte

# Planejar
terraform plan

# Aplicar (requer confirmação)
terraform apply
```

## 4. Conectar ao Servidor

```bash
# Dev
ssh -i vms-dev-key.pem ubuntu@<PUBLIC_IP>

# Clonar repositório
git clone https://github.com/SEU_USUARIO/VMS.git
cd VMS

# Configurar .env
cp .env.example .env
nano .env

# Iniciar serviços
docker-compose up -d
```

## 5. Gerenciar Instâncias

### Desligar Dev (economizar)
```bash
cd terraform/dev
terraform destroy -target=aws_spot_instance_request.dev
# Ou via AWS CLI
aws ec2 stop-instances --instance-ids <INSTANCE_ID>
```

### Ligar Dev
```bash
aws ec2 start-instances --instance-ids <INSTANCE_ID>
```

## Custos Estimados

### Dev (Spot)
- EC2 t3.xlarge Spot: ~$0.03/h = ~$22/mês (24/7)
- EBS 100GB: $8/mês
- Elastic IP: $0 (associado)
- **Total: ~$30/mês**

### Prod
- EC2 x2: ~$240/mês
- RDS Multi-AZ: ~$280/mês
- ALB: ~$25/mês
- **Total: ~$615/mês**

## Troubleshooting

### Erro: Spot instance não criada
```bash
# Verificar preço spot atual
aws ec2 describe-spot-price-history \
  --instance-types t3.xlarge \
  --start-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --product-descriptions "Linux/UNIX" \
  --query 'SpotPriceHistory[0].SpotPrice'
```

### Erro: Key pair não encontrado
```bash
# Listar key pairs
aws ec2 describe-key-pairs

# Criar novo
aws ec2 create-key-pair --key-name vms-dev-key --query 'KeyMaterial' --output text > vms-dev-key.pem
```

## Comandos Úteis

```bash
# Ver estado atual
terraform show

# Ver outputs
terraform output

# Destruir tudo (CUIDADO!)
terraform destroy

# Atualizar apenas um recurso
terraform apply -target=aws_security_group.dev

# Ver plano sem aplicar
terraform plan -out=tfplan
```
