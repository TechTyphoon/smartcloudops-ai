// Secrets Manager secret for RDS credentials with rotation

resource "aws_secretsmanager_secret" "db_secret" {
  name        = "${var.project_name}/rds/credentials"
  description = "RDS credentials for application"
  kms_key_id  = null
}

resource "aws_secretsmanager_secret_version" "db_secret_value" {
  secret_id = aws_secretsmanager_secret.db_secret.id
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

# Additional IAM policy for VPC and Secrets Manager access
resource "aws_iam_role_policy" "rds_rotation_vpc_policy" {
  name = "${var.project_name}-rds-rotation-vpc-policy"
  role = aws_iam_role.rds_rotation_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:AttachNetworkInterface",
          "ec2:DetachNetworkInterface"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecretVersionStage"
        ]
        Resource = aws_secretsmanager_secret.db_secret.arn
      }
    ]
  })
}

# Security group for RDS rotation Lambda
resource "aws_security_group" "rds_rotation_lambda_sg" {
  name   = "${var.project_name}-rds-rotation-lambda-sg"
  vpc_id = aws_vpc.smartcloudops_vpc.id

  # Outbound HTTPS for Secrets Manager API
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-rds-rotation-lambda-sg"
  }
}

# Separate rule to avoid circular dependency
resource "aws_security_group_rule" "lambda_to_rds" {
  type                     = "egress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.db_sg.id
  security_group_id        = aws_security_group.rds_rotation_lambda_sg.id
}

resource "aws_security_group_rule" "rds_from_lambda" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.rds_rotation_lambda_sg.id
  security_group_id        = aws_security_group.db_sg.id
}

resource "aws_lambda_function" "rds_rotation_lambda" {
  function_name = "${var.project_name}-rds-rotation"
  role          = aws_iam_role.rds_rotation_role.arn
  package_type  = "Image"
  image_uri     = "public.ecr.aws/aws-secrets-manager/secrets-manager-rotation-lambdas:postgresql"
  timeout       = 300

  vpc_config {
    subnet_ids         = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]
    security_group_ids = [aws_security_group.rds_rotation_lambda_sg.id]
  }

  environment {
    variables = {
      SECRETS_MANAGER_ENDPOINT = "https://secretsmanager.${var.aws_region}.amazonaws.com"
      EXCLUDE_CHARACTERS       = " %+~`#$&*()|[]{}:;<>?!'/\"\\@"
    }
  }

  depends_on = [aws_iam_role_policy_attachment.rds_rotation_policy]
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

