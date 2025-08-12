// Amazon RDS (PostgreSQL) Multi-AZ with encryption and automated backups

resource "aws_db_subnet_group" "app_db_subnets" {
  name       = "${var.project_name}-db-subnets"
  subnet_ids = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

resource "aws_security_group" "db_sg" {
  name   = "${var.project_name}-db-sg"
  vpc_id = aws_vpc.smartcloudops_vpc.id

  # Allow from ECS service SG
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_service_sg.id]
  }



  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["152.57.28.188/32"]
  }

  tags = {
    Name = "${var.project_name}-db-sg"
  }
}

resource "aws_db_instance" "app_db" {
  identifier                 = "${var.project_name}-db"
  engine                     = "postgres"
  engine_version             = "16"
  instance_class             = var.rds_instance_class
  allocated_storage          = var.rds_allocated_storage
  db_name                    = var.db_name
  username                   = var.db_username
  password                   = random_password.db_password.result
  db_subnet_group_name       = aws_db_subnet_group.app_db_subnets.name
  vpc_security_group_ids     = [aws_security_group.db_sg.id]
  multi_az                   = true
  storage_encrypted          = true
  backup_retention_period    = var.rds_backup_retention_days
  delete_automated_backups   = true
  skip_final_snapshot        = true
  publicly_accessible        = false
  auto_minor_version_upgrade = true
  copy_tags_to_snapshot      = true

  tags = {
    Name = "${var.project_name}-db"
  }
}

