# Smart CloudOps AI - Terraform Outputs
# Phase 1.1: Infrastructure Outputs

# VPC Information
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.smartcloudops_vpc.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.smartcloudops_vpc.cidr_block
}

# Subnet Information
output "public_subnet_1_id" {
  description = "ID of public subnet 1"
  value       = aws_subnet.public_subnet_1.id
}

output "public_subnet_2_id" {
  description = "ID of public subnet 2"
  value       = aws_subnet.public_subnet_2.id
}

# Security Group Information
output "web_security_group_id" {
  description = "ID of the web security group"
  value       = aws_security_group.web_sg.id
}

output "monitoring_security_group_id" {
  description = "ID of the monitoring security group"
  value       = aws_security_group.monitoring_sg.id
}

# EC2 Instance Information
output "monitoring_instance_id" {
  description = "ID of the monitoring EC2 instance"
  value       = aws_instance.ec2_monitoring.id
}

output "monitoring_instance_public_ip" {
  description = "Public IP address of the monitoring instance"
  value       = aws_instance.ec2_monitoring.public_ip
}

output "monitoring_instance_private_ip" {
  description = "Private IP address of the monitoring instance"
  value       = aws_instance.ec2_monitoring.private_ip
}

output "application_instance_id" {
  description = "ID of the application EC2 instance"
  value       = aws_instance.ec2_application.id
}

output "application_instance_public_ip" {
  description = "Public IP address of the application instance"
  value       = aws_instance.ec2_application.public_ip
}

output "application_instance_private_ip" {
  description = "Private IP address of the application instance"
  value       = aws_instance.ec2_application.private_ip
}

# Connection Information
output "ssh_command_monitoring" {
  description = "SSH command to connect to monitoring instance"
  value       = "ssh -i ~/.ssh/${var.project_name}-key.pem ec2-user@${aws_instance.ec2_monitoring.public_ip}"
}

output "ssh_command_application" {
  description = "SSH command to connect to application instance"
  value       = "ssh -i ~/.ssh/${var.project_name}-key.pem ec2-user@${aws_instance.ec2_application.public_ip}"
}

# Service URLs
output "prometheus_url" {
  description = "URL to access Prometheus"
  value       = "http://${aws_instance.ec2_monitoring.public_ip}:9090"
}

output "grafana_url" {
  description = "URL to access Grafana"
  value       = "http://${aws_instance.ec2_monitoring.public_ip}:3001"
}

output "application_url" {
  description = "URL to access the Flask application"
  value       = length(var.domain_name) > 0 ? "https://${var.domain_name}" : "http://${aws_lb.app_alb.dns_name}"
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.app_alb.dns_name
}

output "rds_endpoint" {
  description = "RDS endpoint hostname"
  value       = aws_db_instance.app_db.address
}

# Key Pair Information
output "key_pair_name" {
  description = "Name of the EC2 key pair"
  value       = "smartcloudops-ai-key"
}

# Monitoring Configuration Commands
output "monitoring_setup_command" {
  description = "Command to configure monitoring after deployment"
  value       = "./scripts/configure_monitoring.sh ${aws_instance.ec2_monitoring.public_ip} ${aws_instance.ec2_application.public_ip}"
}

# Comprehensive Access Information
output "access_summary" {
  description = "Complete access information for all services"
  value       = <<-EOT
  
🎉 Smart CloudOps AI Infrastructure Deployed Successfully!

📊 Monitoring Services:
  Prometheus: http://${aws_instance.ec2_monitoring.public_ip}:9090
  Grafana:    http://${aws_instance.ec2_monitoring.public_ip}:3001 (admin/admin)

🚀 Application Services:
  Flask App:  http://${aws_instance.ec2_application.public_ip}:3000
  Node Metrics: http://${aws_instance.ec2_application.public_ip}:9100/metrics

🔑 SSH Access:
  Monitoring: ssh -i ~/.ssh/${var.project_name}-key.pem ec2-user@${aws_instance.ec2_monitoring.public_ip}
  Application: ssh -i ~/.ssh/${var.project_name}-key.pem ec2-user@${aws_instance.ec2_application.public_ip}

⚙️  Configuration:
  Run: ./scripts/configure_monitoring.sh ${aws_instance.ec2_monitoring.public_ip} ${aws_instance.ec2_application.public_ip}

📚 Documentation: See terraform/monitoring-guide.md for detailed setup instructions
  EOT
}