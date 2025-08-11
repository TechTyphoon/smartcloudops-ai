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
resource "aws_secretsmanager_secret_rotation" "db_rotation" {
  rotation_lambda_arn = null
  secret_id           = aws_secretsmanager_secret.db_secret.id
  rotation_rules {
    automatically_after_days = 30
  }
  depends_on = [aws_secretsmanager_secret_version.db_secret_value]
}

// Provide an alternative SSM param built from Secrets Manager values could be added via Lambda; retain SSM param for app consumption.

