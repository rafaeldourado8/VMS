variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "allowed_cidr" {
  description = "CIDR blocks allowed to access"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
