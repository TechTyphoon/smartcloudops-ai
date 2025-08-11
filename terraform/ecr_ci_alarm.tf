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

# GitHub OIDC role to allow CI to push to ECR
data "aws_iam_policy_document" "gh_oidc_assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/token.actions.githubusercontent.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repo}:${var.github_branch}"]
    }
  }
}

data "aws_caller_identity" "current" {}

resource "aws_iam_role" "gh_actions_ecr_role" {
  count              = length(var.github_repo) > 0 ? 1 : 0
  name               = "${var.project_name}-gh-actions-ecr"
  assume_role_policy = data.aws_iam_policy_document.gh_oidc_assume.json
}

data "aws_iam_policy_document" "ecr_push" {
  statement {
    actions = [
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart"
    ]
    resources = [aws_ecr_repository.app_repo.arn]
  }
}

resource "aws_iam_policy" "ecr_push_policy" {
  count  = length(var.github_repo) > 0 ? 1 : 0
  name   = "${var.project_name}-ecr-push-policy"
  policy = data.aws_iam_policy_document.ecr_push.json
}

resource "aws_iam_role_policy_attachment" "gh_ecr_attach" {
  count      = length(var.github_repo) > 0 ? 1 : 0
  role       = aws_iam_role.gh_actions_ecr_role[0].name
  policy_arn = aws_iam_policy.ecr_push_policy[0].arn
}

output "gh_actions_role_arn" {
  description = "GitHub Actions OIDC role ARN for ECR push"
  value       = length(var.github_repo) > 0 ? aws_iam_role.gh_actions_ecr_role[0].arn : null
}

// IAM policy allowing task to read SSM parameter for secrets
resource "aws_iam_policy" "ecs_task_secrets_read" {
  name        = "${var.project_name}-ecs-task-secrets-read"
  description = "Allow ECS task to read SSM parameters and Secrets Manager secrets"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParameterHistory"],
        Resource = aws_ssm_parameter.db_url.arn
      },
      {
        Effect   = "Allow",
        Action   = ["secretsmanager:GetSecretValue"],
        Resource = aws_secretsmanager_secret.db_secret.arn
      },
      {
        Effect = "Allow",
        Action = ["kms:Decrypt"],
        Resource = [
          "arn:aws:kms:${var.aws_region}:${data.aws_caller_identity.current.account_id}:key/*"
        ],
        Condition = {
          StringEquals = {
            "kms:ViaService" = [
              "ssm.${var.aws_region}.amazonaws.com",
              "secretsmanager.${var.aws_region}.amazonaws.com"
            ]
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_secrets_read_attach" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_task_secrets_read.arn
}

// SNS topic for alarms
resource "aws_sns_topic" "ops_alarms" {
  name = "${var.project_name}-ops-alarms"
}

output "ops_alarms_topic_arn" {
  description = "SNS topic ARN for ops alarms"
  value       = aws_sns_topic.ops_alarms.arn
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
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "ALB 5xx errors detected (>5 in 10 minutes) - Critical issue"
  treat_missing_data  = "notBreaching"
  dimensions = {
    LoadBalancer = aws_lb.app_alb.arn_suffix
  }
  alarm_actions = [aws_sns_topic.ops_alarms.arn]
  ok_actions    = [aws_sns_topic.ops_alarms.arn]
}

resource "aws_cloudwatch_metric_alarm" "alb_4xx_high" {
  alarm_name          = "${var.project_name}-alb-4xx-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "HTTPCode_ELB_4XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 25
  alarm_description   = "ALB 4xx errors are high (>25 in 15 minutes)"
  treat_missing_data  = "notBreaching"
  dimensions = {
    LoadBalancer = aws_lb.app_alb.arn_suffix
  }
  alarm_actions = [aws_sns_topic.ops_alarms.arn]
  ok_actions    = [aws_sns_topic.ops_alarms.arn]
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

# Enhanced alarms: ECS task failures and ALB target health
resource "aws_cloudwatch_metric_alarm" "ecs_task_fail" {
  alarm_name          = "${var.project_name}-ecs-task-fail"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "TaskCount"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 0
  alarm_description   = "ECS tasks are failing or stopped unexpectedly"
  treat_missing_data  = "breaching"
  dimensions = {
    ClusterName   = aws_ecs_cluster.app_cluster.name
    ServiceName   = aws_ecs_service.app_service.name
    DesiredStatus = "STOPPED"
  }
  alarm_actions = [aws_sns_topic.ops_alarms.arn]
  ok_actions    = [aws_sns_topic.ops_alarms.arn]
}

resource "aws_cloudwatch_metric_alarm" "alb_target_unhealthy" {
  alarm_name          = "${var.project_name}-alb-target-unhealthy"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "ALB has no healthy targets available"
  treat_missing_data  = "breaching"
  dimensions = {
    TargetGroup  = aws_lb_target_group.app_tg.arn_suffix
    LoadBalancer = aws_lb.app_alb.arn_suffix
  }
  alarm_actions = [aws_sns_topic.ops_alarms.arn]
  ok_actions    = [aws_sns_topic.ops_alarms.arn]
}

resource "aws_cloudwatch_metric_alarm" "ecs_service_desired_vs_running" {
  alarm_name          = "${var.project_name}-ecs-service-capacity"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 3
  metric_name         = "RunningTaskCount"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "ECS service has fewer running tasks than desired"
  treat_missing_data  = "breaching"
  dimensions = {
    ClusterName = aws_ecs_cluster.app_cluster.name
    ServiceName = aws_ecs_service.app_service.name
  }
  alarm_actions = [aws_sns_topic.ops_alarms.arn]
  ok_actions    = [aws_sns_topic.ops_alarms.arn]
}

// Note: RDS automated snapshot retention is configured via backup_retention in rds.tf

