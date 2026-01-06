# 🏗️ Infraestrutura VMS - Terraform

## 📋 Pré-requisitos

- Terraform >= 1.0
- AWS CLI configurado
- Credenciais IAM com permissões adequadas

## 🔐 Configuração IAM

### 1. Criar usuário IAM para Terraform

```bash
aws iam create-user --user-name terraform-vms
```

### 2. Criar política IAM

Crie um arquivo `terraform-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "ecs:*",
        "ecr:*",
        "rds:*",
        "elasticache:*",
        "s3:*",
        "dynamodb:*",
        "iam:*",
        "logs:*",
        "cloudwatch:*",
        "elasticloadbalancing:*"
      ],
      "Resource": "*"
    }
  ]
}
```

Aplicar a política:

```bash
aws iam create-policy --policy-name TerraformVMSPolicy --policy-document file://terraform-policy.json
aws iam attach-user-policy --user-name terraform-vms --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/TerraformVMSPolicy
```

### 3. Criar Access Key

```bash
aws iam create-access-key --user-name terraform-vms
```

Salve o `AccessKeyId` e `SecretAccessKey`.

### 4. Configurar AWS CLI

```bash
aws configure --profile vms-terraform
```

Insira:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-east-1`
- Default output format: `json`

## 🚀 Uso do Terraform

### 1. Criar bucket S3 para state (primeira vez)

```bash
aws s3api create-bucket --bucket vms-terraform-state --region us-east-1
aws s3api put-bucket-versioning --bucket vms-terraform-state --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket vms-terraform-state --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
```

### 2. Criar tabela DynamoDB para locks

```bash
aws dynamodb create-table \
  --table-name vms-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 3. Inicializar Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
```

### 4. Planejar mudanças

```bash
terraform plan
```

### 5. Aplicar infraestrutura

```bash
terraform apply
```

### 6. Destruir infraestrutura (quando necessário)

```bash
terraform destroy
```

## 📁 Estrutura

```
terraform/
├── main.tf              # Provider e backend
├── variables.tf         # Variáveis
├── outputs.tf           # Outputs
├── modules.tf           # Chamada dos módulos
├── ecr.tf              # Repositórios ECR
├── terraform.tfvars    # Valores das variáveis
└── modules/
    ├── networking/     # VPC, subnets, security groups
    ├── database/       # RDS PostgreSQL
    └── cache/          # ElastiCache Redis
```

## 🎯 Recursos Criados

- **VPC** com subnets públicas e privadas
- **Security Groups** para ALB, ECS, RDS e Redis
- **ECR** para imagens Docker (backend, frontend, streaming, ai_detection)
- **RDS PostgreSQL** para banco de dados
- **ElastiCache Redis** para cache

## 📝 Próximos Passos

1. ✅ Configurar IAM e Terraform (Dia 1)
2. ⏳ Configurar ECS Fargate (Dia 2)
3. ⏳ Configurar ALB e domínio (Dia 3)
4. ⏳ Deploy das aplicações (Dia 4-5)
