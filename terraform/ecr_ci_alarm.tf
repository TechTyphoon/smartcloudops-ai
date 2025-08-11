// ECR repository for app image
resource "aws_ecr_repository" "app_repo" {
  name                 = "${var.project_name}-app"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    Name = "${var.project_name}-ecr"
  }
}

// IAM policy allowing task to read SSM parameter for secrets
resource "aws_iam_policy" "ecs_task_ssm_read" {
  name        = "${var.project_name}-ecs-task-ssm-read"
  description = "Allow ECS task to read secure SSM parameters"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParameterHistory"],
        Resource = aws_ssm_parameter.db_url.arn
      },
      {
        Effect   = "Allow",
        Action   = ["kms:Decrypt"],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_ssm_read_attach" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_task_ssm_read.arn
}

// SNS topic for alarms
resource "aws_sns_topic" "ops_alarms" {
  name = "${var.project_name}-ops-alarms"
}

// Example: subscribe email (optional; can be Slack webhook via Lambda later)
variable "alarm_email" {
  description = "Email address to subscribe to SNS alarms"
  type        = string
  default     = ""
}

resource "aws_sns_topic_subscription" "ops_email" {
  count     = length(var.alarm_email) > 0 ? 1 : 0
  topic_arn = aws_sns_topic.ops_alarms.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

// CloudWatch alarms: ALB 5xx high, ECS CPU/Mem high, RDS failover
resource "aws_cloudwatch_metric_alarm" "alb_5xx_high" {
  alarm_name          = "${var.project_name}-alb-5xx-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_ELB_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 10
  dimensions = {
    LoadBalancer = aws_lb.app_alb.arn_suffix
  }
  alarm_actions = [aws_sns_topic.ops_alarms.arn]
}

resource "aws_cloudwatch_metric_alarm" "alb_4xx_high" {
  alarm_name          = "${var.project_name}-alb-4xx-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_ELB_4XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 100
  dimensions = {
    LoadBalancer = aws_lb.app_alb.arn_suffix
  }
  alarm_actions = [aws_sns_topic.ops_alarms.arn]
}

resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  alarm_name          = "${var.project_name}-ecs-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 75
  dimensions = {
    ClusterName = aws_ecs_cluster.app_cluster.name
    ServiceName = aws_ecs_service.app_service.name
  }
  alarm_actions = [aws_sns_topic.ops_alarms.arn]
}

resource "aws_cloudwatch_metric_alarm" "ecs_mem_high" {
  alarm_name          = "${var.project_name}-ecs-mem-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 80
  dimensions = {
    ClusterName = aws_ecs_cluster.app_cluster.name
    ServiceName = aws_ecs_service.app_service.name
  }
  alarm_actions = [aws_sns_topic.ops_alarms.arn]
}

resource "aws_cloudwatch_metric_alarm" "rds_failover" {
  alarm_name          = "${var.project_name}-rds-failover"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Failover"
  namespace           = "AWS/RDS"
  period              = 60
  statistic           = "Sum"
  threshold           = 0
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.app_db.id
  }
  alarm_description = "Alert when RDS failover is detected"
  alarm_actions     = [aws_sns_topic.ops_alarms.arn]
}

// Note: RDS automated snapshot retention is configured via backup_retention in rds.tf

