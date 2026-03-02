# VMS - Development Environment (EC2 Spot)

terraform {
  required_version = ">= 1.0"
  
  backend "s3" {
    bucket = "vms-terraform-state-gtvision"
    key    = "dev/terraform.tfstate"
    region = "us-east-1"
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
  
  default_tags {
    tags = {
      Environment = "dev"
      Project     = "VMS"
      ManagedBy   = "Terraform"
    }
  }
}

variable "aws_region" {
  default = "us-east-1"
}

variable "spot_max_price" {
  description = "Maximum price for spot instance (empty = current spot price)"
  default     = ""
}

variable "key_name" {
  description = "SSH key pair name"
  default     = "vms-dev-key"
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed to SSH"
  type        = string
  default     = "0.0.0.0/0"
}

variable "github_runner_token" {
  description = "GitHub Actions runner token (optional)"
  type        = string
  default     = ""
  sensitive   = true
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "vms-dev-vpc"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "vms-dev-public"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "vms-dev-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = {
    Name = "vms-dev-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Security Group
resource "aws_security_group" "dev" {
  name        = "vms-dev-sg"
  description = "VMS Development Server"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }
  
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "RTSP MediaMTX"
    from_port   = 8554
    to_port     = 8554
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HAProxy Stats"
    from_port   = 8404
    to_port     = 8404
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "vms-dev-sg"
  }
}

# Elastic IP
resource "aws_eip" "dev" {
  domain = "vpc"
  
  tags = {
    Name = "vms-dev-eip"
  }
}

# EC2 Instance (On-Demand - fallback from Spot)
resource "aws_instance" "dev" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.xlarge"
  key_name               = var.key_name
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.dev.id]
  iam_instance_profile   = aws_iam_instance_profile.dev.name
  
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 100
    iops                  = 3000
    throughput            = 125
    delete_on_termination = false
  }
  
  user_data = templatefile("${path.module}/user-data.sh", {
    github_runner_token = var.github_runner_token
  })
  
  tags = {
    Name = "vms-dev"
  }
}

# Associate Elastic IP
resource "aws_eip_association" "dev" {
  instance_id   = aws_instance.dev.id
  allocation_id = aws_eip.dev.id
}

# Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical
  
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# S3 for backups
resource "aws_s3_bucket" "backups" {
  bucket = "vms-dev-backups-${data.aws_caller_identity.current.account_id}"
  
  tags = {
    Name = "vms-dev-backups"
  }
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id
  
  rule {
    id     = "delete-old-backups"
    status = "Enabled"
    
    filter {}
    
    expiration {
      days = 7
    }
  }
}

data "aws_caller_identity" "current" {}

# IAM Role for EC2
resource "aws_iam_role" "dev" {
  name = "vms-dev-ec2-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "dev_s3" {
  name = "vms-dev-s3-policy"
  role = aws_iam_role.dev.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ]
      Resource = [
        aws_s3_bucket.backups.arn,
        "${aws_s3_bucket.backups.arn}/*"
      ]
    }]
  })
}

resource "aws_iam_instance_profile" "dev" {
  name = "vms-dev-instance-profile"
  role = aws_iam_role.dev.name
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "vms-dev-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "CPU utilization is too high"
  
  dimensions = {
    InstanceId = aws_instance.dev.id
  }
}

# Outputs
output "instance_id" {
  description = "EC2 Instance ID"
  value       = aws_instance.dev.id
}

output "public_ip" {
  description = "Elastic IP address"
  value       = aws_eip.dev.public_ip
}

output "ssh_command" {
  description = "SSH command to connect"
  value       = "ssh -i ${var.key_name}.pem ubuntu@${aws_eip.dev.public_ip}"
}

output "frontend_url" {
  description = "Frontend URL"
  value       = "http://${aws_eip.dev.public_ip}"
}

output "backend_url" {
  description = "Backend API URL"
  value       = "http://${aws_eip.dev.public_ip}/api"
}

output "rtsp_url" {
  description = "RTSP MediaMTX URL"
  value       = "rtsp://${aws_eip.dev.public_ip}:8554"
}

output "haproxy_stats" {
  description = "HAProxy Stats URL"
  value       = "http://${aws_eip.dev.public_ip}:8404/stats"
}

output "s3_backup_bucket" {
  description = "S3 bucket for backups"
  value       = aws_s3_bucket.backups.bucket
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "subnet_id" {
  description = "Subnet ID"
  value       = aws_subnet.public.id
}
