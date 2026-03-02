# VMS - Production Environment
# 24/7 HA for 500 cameras

terraform {
  required_version = ">= 1.0"
  
  backend "s3" {
    bucket = "vms-terraform-state-gtvision"
    key    = "prod/terraform.tfstate"
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
  region = "us-east-1"
  
  default_tags {
    tags = {
      Environment = "prod"
      Project     = "VMS"
      ManagedBy   = "Terraform"
    }
  }
}

variable "aws_region" {
  default = "us-east-1"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.1.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "vms-prod-vpc"
  }
}

resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.1.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "vms-prod-public-1"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.1.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "vms-prod-public-2"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "vms-prod-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = {
    Name = "vms-prod-public-rt"
  }
}

resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# Security Groups
resource "aws_security_group" "alb" {
  name        = "vms-prod-alb-sg"
  description = "Security group for ALB"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs" {
  name        = "vms-prod-ecs-sg"
  description = "Security group for ECS tasks"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds" {
  name        = "vms-prod-rds-sg"
  description = "Security group for RDS"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }
}

# RDS Multi-AZ
resource "aws_db_subnet_group" "main" {
  name       = "vms-prod-db-subnet"
  subnet_ids = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

resource "aws_db_instance" "postgres" {
  identifier              = "vms-prod-postgres"
  engine                  = "postgres"
  engine_version          = "15.4"
  instance_class          = "db.r5.2xlarge"
  allocated_storage       = 500
  storage_type            = "gp3"
  iops                    = 12000
  db_name                 = "gtvision_db"
  username                = "gtvision_user"
  password                = random_password.db_password.result
  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [aws_security_group.rds.id]
  multi_az                = true
  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:00-sun:05:00"
  skip_final_snapshot     = false
  final_snapshot_identifier = "vms-prod-final-snapshot"
  
  tags = {
    Name = "vms-prod-postgres"
  }
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

# RDS Read Replicas
resource "aws_db_instance" "postgres_replica_1" {
  identifier             = "vms-prod-postgres-replica-1"
  replicate_source_db    = aws_db_instance.postgres.identifier
  instance_class         = "db.r5.xlarge"
  publicly_accessible    = false
  skip_final_snapshot    = true
  
  tags = {
    Name = "vms-prod-postgres-replica-1"
  }
}

resource "aws_db_instance" "postgres_replica_2" {
  identifier             = "vms-prod-postgres-replica-2"
  replicate_source_db    = aws_db_instance.postgres.identifier
  instance_class         = "db.r5.xlarge"
  publicly_accessible    = false
  skip_final_snapshot    = true
  
  tags = {
    Name = "vms-prod-postgres-replica-2"
  }
}

# ElastiCache Redis Cluster
resource "aws_elasticache_subnet_group" "main" {
  name       = "vms-prod-redis-subnet"
  subnet_ids = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "vms-prod-redis"
  replication_group_description = "VMS Production Redis Cluster"
  engine                     = "redis"
  engine_version             = "7.0"
  node_type                  = "cache.r5.large"
  num_cache_clusters         = 2
  parameter_group_name       = "default.redis7"
  port                       = 6379
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  security_group_ids         = [aws_security_group.ecs.id]
  automatic_failover_enabled = true
  multi_az_enabled           = true
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "vms-prod-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ALB
resource "aws_lb" "main" {
  name               = "vms-prod-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]
  
  enable_deletion_protection = true
}

resource "aws_lb_target_group" "backend_blue" {
  name        = "vms-prod-backend-blue"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  
  health_check {
    path                = "/api/health/"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
  }
}

resource "aws_lb_target_group" "backend_green" {
  name        = "vms-prod-backend-green"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  
  health_check {
    path                = "/api/health/"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend_blue.arn
  }
}

# S3 for recordings
resource "aws_s3_bucket" "recordings" {
  bucket = "vms-prod-recordings-239857123540"
}

resource "aws_s3_bucket_versioning" "recordings" {
  bucket = aws_s3_bucket.recordings.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "recordings" {
  bucket = aws_s3_bucket.recordings.id
  
  rule {
    id     = "archive-old-recordings"
    status = "Enabled"
    
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    
    expiration {
      days = 365
    }
  }
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "vms-prod-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ECS CPU utilization"
  
  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
  }
}

# Outputs
output "alb_dns" {
  value = aws_lb.main.dns_name
}

output "db_endpoint" {
  value     = aws_db_instance.postgres.endpoint
  sensitive = true
}

output "db_replica_1_endpoint" {
  value     = aws_db_instance.postgres_replica_1.endpoint
  sensitive = true
}

output "db_replica_2_endpoint" {
  value     = aws_db_instance.postgres_replica_2.endpoint
  sensitive = true
}

output "redis_endpoint" {
  value = aws_elasticache_replication_group.redis.primary_endpoint_address
}

output "s3_bucket" {
  value = aws_s3_bucket.recordings.bucket
}
