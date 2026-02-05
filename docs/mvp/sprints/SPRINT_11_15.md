# 🎯 SPRINTS 11-15: DEPLOY CLOUD (AWS)

## SPRINT 11: INFRAESTRUTURA TERRAFORM

### Objetivo
Criar infraestrutura AWS reproduzível via Terraform

### Estrutura de Arquivos

```
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── modules/
│   ├── vpc/
│   ├── mediamtx_node/
│   └── monitoring/
└── environments/
    ├── staging/
    └── production/
```

### main.tf

```hcl
terraform {
  required_version = ">= 1.5"
  
  backend "s3" {
    bucket         = "gtvision-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "gtvision-terraform-locks"
    encrypt        = true
  }
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
module "vpc" {
  source = "./modules/vpc"
  
  vpc_cidr = "10.0.0.0/16"
  azs      = ["us-east-1a", "us-east-1b"]
}

# MediaMTX Nodes
module "mediamtx_nodes" {
  source = "./modules/mediamtx_node"
  count  = var.node_count
  
  node_id         = count.index + 1
  vpc_id          = module.vpc.vpc_id
  subnet_id       = module.vpc.private_subnets[count.index % 2]
  instance_type   = var.instance_type
  ebs_volume_size = var.ebs_volume_size
  
  tags = {
    Name        = "mediamtx-node-${count.index + 1}"
    Environment = var.environment
  }
}

# Application Load Balancer
resource "aws_lb" "mediamtx" {
  name               = "gtvision-mediamtx-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets
}

# Target Group (HLS)
resource "aws_lb_target_group" "hls" {
  name     = "gtvision-hls"
  port     = 8888
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id
  
  health_check {
    path                = "/v3/config/global/get"
    port                = 9997
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "mediamtx" {
  name                = "gtvision-mediamtx-asg"
  vpc_zone_identifier = module.vpc.private_subnets
  min_size            = var.min_nodes
  max_size            = var.max_nodes
  desired_capacity    = var.node_count
  
  launch_template {
    id      = aws_launch_template.mediamtx.id
    version = "$Latest"
  }
  
  tag {
    key                 = "Name"
    value               = "mediamtx-node"
    propagate_at_launch = true
  }
}
```

### modules/mediamtx_node/main.tf

```hcl
resource "aws_instance" "mediamtx" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = var.subnet_id
  
  vpc_security_group_ids = [aws_security_group.mediamtx.id]
  iam_instance_profile   = aws_iam_instance_profile.mediamtx.name
  
  user_data = templatefile("${path.module}/user_data.sh", {
    node_id     = var.node_id
    s3_bucket   = var.s3_bucket
    environment = var.environment
  })
  
  root_block_device {
    volume_type = "gp3"
    volume_size = 50
    encrypted   = true
  }
  
  tags = var.tags
}

# EBS Volume para gravações
resource "aws_ebs_volume" "recordings" {
  availability_zone = aws_instance.mediamtx.availability_zone
  size              = var.ebs_volume_size
  type              = "gp3"
  iops              = 3000
  throughput        = 125
  encrypted         = true
  
  tags = merge(var.tags, {
    Name = "mediamtx-recordings-${var.node_id}"
  })
}

resource "aws_volume_attachment" "recordings" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.recordings.id
  instance_id = aws_instance.mediamtx.id
}

# Security Group
resource "aws_security_group" "mediamtx" {
  name        = "mediamtx-node-${var.node_id}"
  description = "MediaMTX Node Security Group"
  vpc_id      = var.vpc_id
  
  # RTSP
  ingress {
    from_port   = 8554
    to_port     = 8554
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  
  # HLS
  ingress {
    from_port   = 8888
    to_port     = 8888
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  
  # API
  ingress {
    from_port   = 9997
    to_port     = 9997
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### user_data.sh

```bash
#!/bin/bash
set -e

# Montar EBS
mkfs -t ext4 /dev/sdf
mkdir -p /recordings
mount /dev/sdf /recordings
echo "/dev/sdf /recordings ext4 defaults,nofail 0 2" >> /etc/fstab

# Instalar Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Baixar configuração do S3
aws s3 cp s3://${s3_bucket}/mediamtx.yml /opt/mediamtx.yml

# Iniciar MediaMTX
docker run -d \
  --name mediamtx \
  --restart unless-stopped \
  -p 8554:8554 \
  -p 8888:8888 \
  -p 9997:9997 \
  -v /opt/mediamtx.yml:/mediamtx.yml:ro \
  -v /recordings:/recordings \
  bluenviron/mediamtx:latest-ffmpeg

# CloudWatch Agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i amazon-cloudwatch-agent.deb

cat > /opt/aws/amazon-cloudwatch-agent/etc/config.json <<EOF
{
  "metrics": {
    "namespace": "GTVision/MediaMTX",
    "metrics_collected": {
      "disk": {
        "measurement": [
          {"name": "used_percent", "rename": "DiskUsage"}
        ],
        "metrics_collection_interval": 60,
        "resources": ["/recordings"]
      },
      "cpu": {
        "measurement": [
          {"name": "cpu_usage_active", "rename": "CPUUsage"}
        ],
        "metrics_collection_interval": 60
      }
    }
  }
}
EOF

/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json \
  -s
```

### variables.tf

```hcl
variable "aws_region" {
  default = "us-east-1"
}

variable "environment" {
  type = string
}

variable "node_count" {
  type    = number
  default = 10
}

variable "instance_type" {
  type    = string
  default = "t3.large"
}

variable "ebs_volume_size" {
  type    = number
  default = 3000  # 3TB
}

variable "min_nodes" {
  type    = number
  default = 5
}

variable "max_nodes" {
  type    = number
  default = 20
}
```

### Deploy

```bash
cd terraform/environments/production

terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

---

## SPRINT 12: DEPLOY AUTOMATIZADO

### AMI Customizada (Packer)

```hcl
# packer/mediamtx.pkr.hcl
source "amazon-ebs" "mediamtx" {
  ami_name      = "gtvision-mediamtx-{{timestamp}}"
  instance_type = "t3.medium"
  region        = "us-east-1"
  source_ami_filter {
    filters = {
      name                = "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"]
  }
  ssh_username = "ubuntu"
}

build {
  sources = ["source.amazon-ebs.mediamtx"]
  
  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y docker.io awscli",
      "sudo systemctl enable docker",
      "sudo docker pull bluenviron/mediamtx:latest-ffmpeg"
    ]
  }
}
```

### Build AMI

```bash
packer build packer/mediamtx.pkr.hcl
```

---

## SPRINT 13: MONITORAMENTO CLOUDWATCH

### CloudWatch Dashboard

```hcl
resource "aws_cloudwatch_dashboard" "mediamtx" {
  dashboard_name = "GTVision-MediaMTX"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["GTVision/MediaMTX", "DiskUsage", {stat = "Average"}],
            [".", "CPUUsage", {stat = "Average"}]
          ]
          period = 300
          stat   = "Average"
          region = "us-east-1"
          title  = "Node Health"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/EC2", "NetworkIn", {stat = "Sum"}],
            [".", "NetworkOut", {stat = "Sum"}]
          ]
          period = 300
          stat   = "Sum"
          region = "us-east-1"
          title  = "Network Traffic"
        }
      }
    ]
  })
}
```

### Alarmes

```hcl
resource "aws_cloudwatch_metric_alarm" "disk_full" {
  alarm_name          = "mediamtx-disk-full"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DiskUsage"
  namespace           = "GTVision/MediaMTX"
  period              = 300
  statistic           = "Average"
  threshold           = 90
  alarm_description   = "Disk usage > 90%"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "mediamtx-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUsage"
  namespace           = "GTVision/MediaMTX"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "CPU usage > 80%"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "aws_sns_topic" "alerts" {
  name = "gtvision-alerts"
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = "ops@gtvision.com"
}
```

---

## SPRINT 14: BACKUP PARA S3

### Lifecycle Policy

```hcl
resource "aws_s3_bucket" "recordings" {
  bucket = "gtvision-recordings-backup"
}

resource "aws_s3_bucket_lifecycle_configuration" "recordings" {
  bucket = aws_s3_bucket.recordings.id
  
  rule {
    id     = "archive-old-recordings"
    status = "Enabled"
    
    transition {
      days          = 7
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 30
      storage_class = "GLACIER"
    }
    
    expiration {
      days = 365
    }
  }
}
```

### Script de Sincronização

```bash
#!/bin/bash
# /opt/scripts/sync_to_s3.sh

DATE_YESTERDAY=$(date -d '1 day ago' +%Y-%m-%d)
S3_BUCKET="s3://gtvision-recordings-backup"

# Sincronizar gravações de ontem
for cam_dir in /recordings/cam_*; do
  cam_id=$(basename $cam_dir)
  
  if [ -d "$cam_dir/$DATE_YESTERDAY" ]; then
    echo "Syncing $cam_id/$DATE_YESTERDAY to S3..."
    
    aws s3 sync "$cam_dir/$DATE_YESTERDAY" \
      "$S3_BUCKET/$cam_id/$DATE_YESTERDAY/" \
      --storage-class STANDARD \
      --only-show-errors
    
    echo "✓ $cam_id/$DATE_YESTERDAY synced"
  fi
done

# Limpar local após sync (opcional)
# find /recordings -type d -mtime +7 -exec rm -rf {} \;
```

### Cron Job

```bash
# Adicionar ao crontab
0 2 * * * /opt/scripts/sync_to_s3.sh >> /var/log/s3-sync.log 2>&1
```

### Restore Script

```bash
#!/bin/bash
# restore_from_s3.sh

CAMERA_ID=$1
DATE=$2

aws s3 sync \
  s3://gtvision-recordings-backup/cam_$CAMERA_ID/$DATE/ \
  /recordings/cam_$CAMERA_ID/$DATE/

echo "✓ Restored cam_$CAMERA_ID/$DATE"
```

---

## SPRINT 15: TESTES DE PRODUÇÃO AWS

### Checklist de Deploy

```bash
# 1. Deploy infraestrutura
cd terraform/environments/production
terraform apply

# 2. Verificar nós
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=mediamtx-node" \
  --query 'Reservations[].Instances[].[InstanceId,State.Name,PrivateIpAddress]'

# 3. Provisionar 120 câmeras
for i in {1..120}; do
  curl -X POST http://orchestrator.gtvision.com/cameras/$i/allocate
done

# 4. Monitorar CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace GTVision/MediaMTX \
  --metric-name DiskUsage \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average

# 5. Teste de failover
# Terminar 1 instância
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0

# Verificar redistribuição automática (ASG cria nova instância)
```

### Relatório de Custos

```
EC2 (10× t3.large):
  - On-Demand: $0.0832/h × 10 × 730h = $607/mês
  - Reserved (1y): $0.0499/h × 10 × 730h = $364/mês

EBS (10× 3TB gp3):
  - Storage: $0.08/GB × 3000GB × 10 = $2,400/mês
  - IOPS: incluído (3000 IOPS base)

Data Transfer:
  - Inbound: grátis
  - Outbound: ~500GB/mês = $45/mês

S3 Backup:
  - Standard (7d): 3TB × $0.023 = $69/mês
  - Glacier (30d): 12TB × $0.004 = $48/mês

CloudWatch:
  - Métricas: ~$30/mês
  - Logs: ~$20/mês

TOTAL (On-Demand): ~$3,219/mês
TOTAL (Reserved): ~$2,976/mês
```

### Otimizações de Custo

1. **Reserved Instances**: -40% no EC2
2. **Savings Plans**: -30% no EC2
3. **EBS gp3 vs gp2**: -20% no storage
4. **S3 Intelligent-Tiering**: -30% no backup
5. **Spot Instances** (não recomendado para produção)

**Custo otimizado**: ~$2,500/mês
