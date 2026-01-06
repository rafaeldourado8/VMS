variable "aws_region" {
  description = "Região AWS para deploy"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Nome do projeto"
  type        = string
  default     = "vms"
}

variable "max_cameras" {
  description = "Número máximo de câmeras simultâneas"
  type        = number
  default     = 4
}

variable "max_users" {
  description = "Número máximo de usuários simultâneos"
  type        = number
  default     = 4
}
