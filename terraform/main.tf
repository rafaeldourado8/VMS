terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "vms-terraform-state"
    key            = "vms/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "vms-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "VMS"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
