# Optional Slack Forwarder Lambda for SNS Alarms

locals {
  slack_enabled = var.enable_slack_notifications && length(var.slack_webhook_secret_name) > 0
}

# Look up Slack webhook secret by name
data "aws_secretsmanager_secret" "slack" {
  count = local.slack_enabled ? 1 : 0
  name  = var.slack_webhook_secret_name
}

resource "aws_iam_role" "slack_lambda_role" {
  count = local.slack_enabled ? 1 : 0
  name  = "${var.project_name}-slack-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = { Service = "lambda.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_cloudwatch_log_group" "slack_lambda_lg" {
  count             = local.slack_enabled ? 1 : 0
  name              = "/aws/lambda/${var.project_name}-slack-forwarder"
  retention_in_days = 14
}

resource "aws_iam_role_policy" "slack_lambda_policy" {
  count = local.slack_enabled ? 1 : 0
  name  = "${var.project_name}-slack-lambda-policy"
  role  = aws_iam_role.slack_lambda_role[0].id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect : "Allow",
        Action : ["secretsmanager:GetSecretValue"],
        Resource : data.aws_secretsmanager_secret.slack[0].arn
      },
      {
        Effect : "Allow",
        Action : ["logs:CreateLogStream", "logs:PutLogEvents"],
        Resource : "${aws_cloudwatch_log_group.slack_lambda_lg[0].arn}:*"
      }
    ]
  })
}

resource "aws_lambda_function" "slack_forwarder" {
  count         = local.slack_enabled ? 1 : 0
  function_name = "${var.project_name}-slack-forwarder"
  role          = aws_iam_role.slack_lambda_role[0].arn
  runtime       = "python3.10"
  handler       = "lambda_function.handler"
  filename      = "${path.module}/lambda/slack_forwarder.zip"
  timeout       = 10
  depends_on    = [aws_cloudwatch_log_group.slack_lambda_lg]

  environment {
    variables = {
      SLACK_SECRET_NAME = var.slack_webhook_secret_name
      AWS_REGION        = var.aws_region
    }
  }
}

resource "aws_lambda_permission" "allow_sns_invoke" {
  count         = local.slack_enabled ? 1 : 0
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.slack_forwarder[0].function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.ops_alarms.arn
}

resource "aws_sns_topic_subscription" "slack_sub" {
  count     = local.slack_enabled ? 1 : 0
  topic_arn = aws_sns_topic.ops_alarms.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.slack_forwarder[0].arn
}

