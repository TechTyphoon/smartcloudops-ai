# VPC Module Outputs
# Phase 3 Week 5: Infrastructure as Code (IaC) - VPC Module Outputs

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}

output "vpc_arn" {
  description = "VPC ARN"
  value       = aws_vpc.main.arn
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "Database subnet IDs"
  value       = aws_subnet.database[*].id
}

output "database_subnet_group_name" {
  description = "Database subnet group name"
  value       = try(aws_db_subnet_group.main.name, "")
}

output "elasticache_subnet_group_name" {
  description = "ElastiCache subnet group name"
  value       = aws_elasticache_subnet_group.main.name
}

output "internet_gateway_id" {
  description = "Internet Gateway ID"
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_ids" {
  description = "NAT Gateway IDs"
  value       = aws_nat_gateway.main[*].id
}

output "public_route_table_id" {
  description = "Public route table ID"
  value       = aws_route_table.public.id
}

output "private_route_table_ids" {
  description = "Private route table IDs"
  value       = aws_route_table.private[*].id
}

output "database_route_table_id" {
  description = "Database route table ID"
  value       = try(aws_route_table.database[0].id, "")
}

output "vpc_endpoint_s3_id" {
  description = "S3 VPC Endpoint ID"
  value       = try(aws_vpc_endpoint.s3[0].id, "")
}

output "vpc_endpoint_ecr_dkr_id" {
  description = "ECR DKR VPC Endpoint ID"
  value       = try(aws_vpc_endpoint.ecr_dkr[0].id, "")
}

output "vpc_endpoint_ecr_api_id" {
  description = "ECR API VPC Endpoint ID"
  value       = try(aws_vpc_endpoint.ecr_api[0].id, "")
}
