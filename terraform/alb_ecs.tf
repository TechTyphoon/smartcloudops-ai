// ALB + ECS Fargate service with HTTPS enforcement

resource "aws_cloudwatch_log_group" "ecs_app_lg" {
  name              = "/ecs/${var.project_name}-app"
  retention_in_days = 14
}

resource "aws_lb" "app_alb" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.web_sg.id]
  subnets            = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]

  # Optional access logs to S3
  dynamic "access_logs" {
    for_each = var.enable_alb_access_logs ? [1] : []
    content {
      bucket  = aws_s3_bucket.alb_access_logs[0].bucket
      enabled = true
      prefix  = "alb-access-logs"
    }
  }

  tags = {
    Name = "${var.project_name}-alb"
  }
}

resource "aws_lb_target_group" "app_tg" {
  name        = "${var.project_name}-tg"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.smartcloudops_vpc.id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    interval            = 30
    timeout             = 5
    matcher             = "200"
  }
}

# Second target group for blue/green deployments
resource "aws_lb_target_group" "app_tg_green" {
  name        = "${var.project_name}-tg-green"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.smartcloudops_vpc.id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    interval            = 30
    timeout             = 5
    matcher             = "200"
  }
}

// ACM certificate (DNS validation). If domain_name not provided, skip creation.
resource "aws_acm_certificate" "app_cert" {
  count             = length(var.domain_name) > 0 ? 1 : 0
  domain_name       = var.domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "cert_validation" {
  count   = length(var.domain_name) > 0 ? 1 : 0
  name    = one(aws_acm_certificate.app_cert[0].domain_validation_options).resource_record_name
  type    = one(aws_acm_certificate.app_cert[0].domain_validation_options).resource_record_type
  zone_id = var.hosted_zone_id
  records = [one(aws_acm_certificate.app_cert[0].domain_validation_options).resource_record_value]
  ttl     = 60
}

resource "aws_acm_certificate_validation" "app_cert_validation" {
  count                   = length(var.domain_name) > 0 ? 1 : 0
  certificate_arn         = aws_acm_certificate.app_cert[0].arn
  validation_record_fqdns = [aws_route53_record.cert_validation[0].fqdn]
}

resource "aws_lb_listener" "http_redirect" {
  count             = length(var.domain_name) > 0 ? 1 : 0
  load_balancer_arn = aws_lb.app_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "http_plain" {
  count             = length(var.domain_name) == 0 ? 1 : 0
  load_balancer_arn = aws_lb.app_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "forward"
    forward {
      target_group {
        arn    = aws_lb_target_group.app_tg_green.arn
        weight = 1
      }
      stickiness {
        enabled  = false
        duration = 0
      }
    }
  }
}

resource "aws_lb_listener" "https" {
  count             = length(var.domain_name) > 0 ? 1 : 0
  load_balancer_arn = aws_lb.app_alb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate_validation.app_cert_validation[0].certificate_arn

  default_action {
    type = "forward"
    forward {
      target_group {
        arn    = aws_lb_target_group.app_tg_green.arn
        weight = 1
      }
      stickiness {
        enabled  = false
        duration = 0
      }
    }
  }
}

# Route53 alias record to ALB when domain_name provided
resource "aws_route53_record" "app_alias" {
  count   = length(var.domain_name) > 0 ? 1 : 0
  zone_id = var.hosted_zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_lb.app_alb.dns_name
    zone_id                = aws_lb.app_alb.zone_id
    evaluate_target_health = true
  }
}

resource "aws_ecs_cluster" "app_cluster" {
  name = "${var.project_name}-cluster"
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project_name}-ecs-exec-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_exec_logs" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ssm_parameter" "db_url" {
  name  = "/smartcloudops/prod/database/url"
  type  = "SecureString"
  value = "postgresql+psycopg2://cloudops:${random_password.db_password.result}@${aws_db_instance.app_db.address}:5432/${var.db_name}"
  tags = {
    Environment = var.environment
  }
}

resource "random_password" "db_password" {
  length  = 20
  special = false
  upper   = true
  lower   = true
  numeric = true
}

# Validation: Recommend Secrets Manager for production
locals {
  is_production     = var.environment == "prod" || var.environment == "production"
  using_ssm_in_prod = local.is_production && !var.use_secrets_manager_for_db
}

# Warning for SSM usage in production
resource "null_resource" "ssm_prod_warning" {
  count = local.using_ssm_in_prod ? 1 : 0

  triggers = {
    warning = "WARNING: Using SSM Parameter Store for DATABASE_URL in production. Consider setting use_secrets_manager_for_db=true for automatic credential rotation."
  }

  provisioner "local-exec" {
    command = "echo 'WARNING: Using SSM Parameter Store for DATABASE_URL in production. Consider setting use_secrets_manager_for_db=true for automatic credential rotation.'"
  }
}

resource "aws_ecs_task_definition" "app_task" {
  family                   = "${var.project_name}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = "${aws_ecr_repository.app_repo.repository_url}:latest"
      essential = true
      portMappings = [
        { containerPort = 3000, hostPort = 3000, protocol = "tcp" }
      ]
      environment = [
        { name = "FLASK_ENV", value = "production" },
        { name = "FLASK_PORT", value = "3000" },
        { name = "PROMETHEUS_URL", value = "http://localhost:9090" }
      ]
      secrets = var.use_secrets_manager_for_db ? [
        { name = "DATABASE_URL", valueFrom = aws_secretsmanager_secret.db_secret.arn }
        ] : [
        { name = "DATABASE_URL", valueFrom = aws_ssm_parameter.db_url.arn }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_app_lg.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "app"
        }
      }
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:3000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 30
      }
    }
  ])
}

resource "aws_security_group" "ecs_service_sg" {
  name   = "${var.project_name}-ecs-sg"
  vpc_id = aws_vpc.smartcloudops_vpc.id

  # Outbound to anywhere for dependencies
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["152.57.28.188/32"]
  }

  tags = {
    Name = "${var.project_name}-ecs-sg"
  }
}

resource "aws_ecs_service" "app_service" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.app_cluster.id
  task_definition = aws_ecs_task_definition.app_task.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  dynamic "deployment_controller" {
    for_each = [1]
    content {
      type = var.enable_blue_green ? "CODE_DEPLOY" : "ECS"
    }
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  network_configuration {
    subnets         = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]
    security_groups = [aws_security_group.ecs_service_sg.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app_tg.arn
    container_name   = "app"
    container_port   = 3000
  }

  # Implicit dependencies via target group and listeners
}

resource "aws_appautoscaling_target" "ecs_scaling_target" {
  max_capacity       = 6
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.app_cluster.name}/${aws_ecs_service.app_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu_scale_out" {
  name               = "${var.project_name}-cpu-scale-out"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_scaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_scaling_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_scaling_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 60
    scale_in_cooldown  = 120
    scale_out_cooldown = 60
  }
}

resource "aws_appautoscaling_policy" "mem_scale_out" {
  name               = "${var.project_name}-mem-scale-out"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_scaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_scaling_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_scaling_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value       = 70
    scale_in_cooldown  = 120
    scale_out_cooldown = 60
  }
}

