output "vpc_id" {
  description = "ID da VPC criada"
  value       = module.networking.vpc_id
}

output "ecr_repository_urls" {
  description = "URLs dos repositórios ECR"
  value = {
    backend      = aws_ecr_repository.backend.repository_url
    frontend     = aws_ecr_repository.frontend.repository_url
    streaming    = aws_ecr_repository.streaming.repository_url
    ai_detection = aws_ecr_repository.ai_detection.repository_url
  }
}

output "rds_endpoint" {
  description = "Endpoint do RDS PostgreSQL"
  value       = module.database.rds_endpoint
  sensitive   = true
}

output "elasticache_endpoint" {
  description = "Endpoint do ElastiCache Redis"
  value       = module.cache.redis_endpoint
}
