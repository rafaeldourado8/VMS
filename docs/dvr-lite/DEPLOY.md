# 🚀 DVR-Lite - Deploy AWS

Guia completo para deploy na AWS.

---

## 📋 Pré-requisitos

- Conta AWS ativa
- AWS CLI instalado
- Docker instalado
- Domínio registrado (opcional)

---

## 🏗️ Infraestrutura

### 1. IAM Setup
```bash
# Criar usuário para deploy
aws iam create-user --user-name dvr-lite-deploy

# Criar policy
aws iam create-policy --policy-name DVRLitePolicy --policy-document file://iam-policy.json

# Anexar policy
aws iam attach-user-policy --user-name dvr-lite-deploy --policy-arn arn:aws:iam::ACCOUNT:policy/DVRLitePolicy

# Criar access key
aws iam create-access-key --user-name dvr-lite-deploy
```

### 2. VPC e Networking
```bash
# Criar VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Criar subnets
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24 --availability-zone us-east-1a
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.2.0/24 --availability-zone us-east-1b

# Criar Internet Gateway
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --vpc-id vpc-xxx --internet-gateway-id igw-xxx
```

### 3. Security Groups
```bash
# Backend SG
aws ec2 create-security-group --group-name dvr-backend --description "DVR Backend" --vpc-id vpc-xxx
aws ec2 authorize-security-group-ingress --group-id sg-xxx --protocol tcp --port 8000 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id sg-xxx --protocol tcp --port 8888 --cidr 0.0.0.0/0

# Database SG
aws ec2 create-security-group --group-name dvr-database --description "DVR Database" --vpc-id vpc-xxx
aws ec2 authorize-security-group-ingress --group-id sg-xxx --protocol tcp --port 5432 --source-group sg-backend
```

---

## 💾 Storage (S3)

### Criar Buckets
```bash
# Bucket para gravações
aws s3 mb s3://dvr-lite-recordings

# Bucket para clipes
aws s3 mb s3://dvr-lite-clips

# Configurar lifecycle (7 dias)
aws s3api put-bucket-lifecycle-configuration --bucket dvr-lite-recordings --lifecycle-configuration file://lifecycle.json
```

### lifecycle.json
```json
{
  "Rules": [{
    "Id": "DeleteOldRecordings",
    "Status": "Enabled",
    "Prefix": "recordings/",
    "Expiration": {
      "Days": 7
    }
  }]
}
```

---

## 🗄️ Database (RDS)

```bash
# Criar subnet group
aws rds create-db-subnet-group --db-subnet-group-name dvr-subnet-group --subnet-ids subnet-xxx subnet-yyy

# Criar instância
aws rds create-db-instance \
  --db-instance-identifier dvr-postgres \
  --db-instance-class db.t3.small \
  --engine postgres \
  --master-username admin \
  --master-user-password CHANGE_ME \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxx \
  --db-subnet-group-name dvr-subnet-group \
  --backup-retention-period 7
```

---

## ⚡ Cache (ElastiCache)

```bash
# Criar subnet group
aws elasticache create-cache-subnet-group --cache-subnet-group-name dvr-cache-subnet --subnet-ids subnet-xxx subnet-yyy

# Criar cluster Redis
aws elasticache create-cache-cluster \
  --cache-cluster-id dvr-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --cache-subnet-group-name dvr-cache-subnet \
  --security-group-ids sg-xxx
```

---

## 🖥️ Compute (EC2)

### Opção A: EC2 com Docker Compose

```bash
# Criar instância
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.large \
  --key-name my-key \
  --security-group-ids sg-xxx \
  --subnet-id subnet-xxx \
  --user-data file://user-data.sh

# SSH
ssh -i my-key.pem ec2-user@IP

# Instalar Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repo
git clone https://github.com/your-repo/vms.git
cd vms
git checkout dvr-lite

# Configurar .env
cp .env.example .env
nano .env

# Deploy
docker-compose up -d
```

### Opção B: ECS Fargate

```bash
# Criar cluster
aws ecs create-cluster --cluster-name dvr-lite

# Criar task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Criar service
aws ecs create-service \
  --cluster dvr-lite \
  --service-name dvr-backend \
  --task-definition dvr-backend:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

---

## ⚖️ Load Balancer

```bash
# Criar ALB
aws elbv2 create-load-balancer \
  --name dvr-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx

# Criar target group
aws elbv2 create-target-group \
  --name dvr-targets \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxx \
  --health-check-path /health

# Criar listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

---

## 🔒 SSL/TLS

```bash
# Solicitar certificado
aws acm request-certificate \
  --domain-name dvr.example.com \
  --validation-method DNS

# Criar listener HTTPS
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:... \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

---

## 🌐 DNS (Route 53)

```bash
# Criar hosted zone
aws route53 create-hosted-zone --name example.com --caller-reference $(date +%s)

# Criar record
aws route53 change-resource-record-sets --hosted-zone-id Z123 --change-batch file://dns-record.json
```

---

## 📊 Monitoring

```bash
# Criar alarme CPU
aws cloudwatch put-metric-alarm \
  --alarm-name dvr-high-cpu \
  --alarm-description "CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# Criar dashboard
aws cloudwatch put-dashboard --dashboard-name DVR-Lite --dashboard-body file://dashboard.json
```

---

## 🔄 CI/CD (GitHub Actions)

### .github/workflows/deploy.yml
```yaml
name: Deploy to AWS

on:
  push:
    branches: [dvr-lite]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Deploy to EC2
        run: |
          ssh -i key.pem ec2-user@${{ secrets.EC2_IP }} << 'EOF'
            cd /home/ec2-user/vms
            git pull
            docker-compose down
            docker-compose up -d --build
          EOF
```

---

## ✅ Checklist de Deploy

- [ ] IAM configurado
- [ ] VPC e subnets criados
- [ ] Security groups configurados
- [ ] S3 buckets criados
- [ ] RDS PostgreSQL criado
- [ ] ElastiCache Redis criado
- [ ] EC2/ECS configurado
- [ ] ALB configurado
- [ ] SSL/TLS configurado
- [ ] DNS configurado
- [ ] Monitoring configurado
- [ ] CI/CD configurado
- [ ] Backup configurado
- [ ] Testes de carga realizados

---

## 🧪 Testes

```bash
# Health check
curl https://dvr.example.com/health

# Streaming
curl https://dvr.example.com/api/cameras/

# Playback
curl https://dvr.example.com/api/recordings/
```

---

## 💰 Custos Estimados

Ver [AWS_COSTS.md](AWS_COSTS.md)

---

## 🔧 Troubleshooting

### Logs
```bash
# EC2
ssh ec2-user@IP
docker-compose logs -f

# CloudWatch
aws logs tail /aws/ec2/dvr-lite --follow
```

### Common Issues
- **502 Bad Gateway:** Verificar security groups
- **Slow streaming:** Verificar bandwidth
- **High costs:** Verificar data transfer
