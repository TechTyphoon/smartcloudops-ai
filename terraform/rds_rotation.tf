// Secrets Manager secret for RDS credentials with rotation

resource "aws_secretsmanager_secret" "db_secret" {
  name        = "${var.project_name}/rds/credentials"
  description = "RDS credentials for application"
  kms_key_id  = null
}

resource "aws_secretsmanager_secret_version" "db_secret_value" {
  secret_id     = aws_secretsmanager_secret.db_secret.id
  secret_string = jsonencode({
    username = var.db_username,
    password = random_password.db_password.result,
    host     = aws_db_instance.app_db.address,
    port     = 5432,
    dbname   = var.db_name
  })
}

// Optional: attach rotation lambda and schedule. Placeholder for managed rotation
// For brevity, we set rotation rules only; lambda setup can be added later.
data "aws_iam_policy_document" "rds_rotation_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "rds_rotation_role" {
  name               = "${var.project_name}-rds-rotation-role"
  assume_role_policy = data.aws_iam_policy_document.rds_rotation_assume.json
}

resource "aws_iam_role_policy_attachment" "rds_rotation_policy" {
  role       = aws_iam_role.rds_rotation_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSSecretsManagerRotationLambdaBasic"
}

resource "aws_lambda_function" "rds_rotation_lambda" {
  filename         = null
  s3_bucket        = null
  s3_key           = null
  function_name    = "${var.project_name}-rds-rotation"
  role             = aws_iam_role.rds_rotation_role.arn
  handler          = "SecretsManagerRDSPostgreSQLRotationMultiUser"
  runtime          = "python3.10"
  package_type     = "Image"
  image_uri        = "public.ecr.aws/aws-secrets-manager/secrets-manager-rotation-lambdas:postgresql-rotation"
  timeout          = 300
  depends_on       = [aws_iam_role_policy_attachment.rds_rotation_policy]
}

resource "aws_secretsmanager_secret_rotation" "db_rotation" {
  rotation_lambda_arn = aws_lambda_function.rds_rotation_lambda.arn
  secret_id           = aws_secretsmanager_secret.db_secret.id
  rotation_rules {
    automatically_after_days = 30
  }
  depends_on = [aws_secretsmanager_secret_version.db_secret_value]
}

// Provide an alternative SSM param built from Secrets Manager values could be added via Lambda; retain SSM param for app consumption.

