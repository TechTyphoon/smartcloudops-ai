#!/bin/bash

# SmartCloudOps AI - AWS Deployment Script
# This script deploys the SmartCloudOps AI application to AWS ECS/Fargate

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="smartcloudops-ai"
VERSION="3.1.0"
AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPOSITORY="${PROJECT_NAME}"
CLUSTER_NAME="${PROJECT_NAME}-cluster"
SERVICE_NAME="${PROJECT_NAME}-service"
TASK_DEFINITION_NAME="${PROJECT_NAME}-task"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        error "AWS CLI is not installed. Please install it first."
    fi
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install it first."
    fi
    
    # Check if required environment variables are set
    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        error "AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables."
    fi
    
    # Check if required files exist
    if [ ! -f "docker-compose.production.yml" ]; then
        error "docker-compose.production.yml not found."
    fi
    
    if [ ! -f "configs/env.production" ]; then
        error "configs/env.production not found."
    fi
    
    log "Prerequisites check passed!"
}

# Build and push Docker image to ECR
build_and_push_image() {
    log "Building and pushing Docker image to ECR..."
    
    # Get ECR login token
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    
    # Create ECR repository if it doesn't exist
    aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION 2>/dev/null || {
        log "Creating ECR repository: $ECR_REPOSITORY"
        aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION
    }
    
    # Build Docker image
    log "Building Docker image..."
    docker build -t $ECR_REPOSITORY:$VERSION .
    docker tag $ECR_REPOSITORY:$VERSION $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$VERSION
    
    # Push to ECR
    log "Pushing image to ECR..."
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$VERSION
    
    log "Docker image pushed successfully!"
}

# Create ECS cluster
create_ecs_cluster() {
    log "Creating ECS cluster..."
    
    # Check if cluster exists
    if aws ecs describe-clusters --clusters $CLUSTER_NAME --region $AWS_REGION --query 'clusters[0].status' --output text 2>/dev/null | grep -q "ACTIVE"; then
        log "ECS cluster $CLUSTER_NAME already exists."
    else
        aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $AWS_REGION
        log "ECS cluster $CLUSTER_NAME created successfully!"
    fi
}

# Create task definition
create_task_definition() {
    log "Creating ECS task definition..."
    
    # Create task definition JSON
    cat > task-definition.json << EOF
{
    "family": "$TASK_DEFINITION_NAME",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "1024",
    "memory": "2048",
    "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
    "taskRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskRole",
    "containerDefinitions": [
        {
            "name": "$PROJECT_NAME",
            "image": "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$VERSION",
            "portMappings": [
                {
                    "containerPort": 5000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {"name": "FLASK_ENV", "value": "production"},
                {"name": "FLASK_PORT", "value": "5000"},
                {"name": "AWS_REGION", "value": "$AWS_REGION"}
            ],
            "secrets": [
                {"name": "DATABASE_URL", "valueFrom": "arn:aws:ssm:$AWS_REGION:$AWS_ACCOUNT_ID:parameter/smartcloudops/database_url"},
                {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:ssm:$AWS_REGION:$AWS_ACCOUNT_ID:parameter/smartcloudops/openai_api_key"},
                {"name": "GEMINI_API_KEY", "valueFrom": "arn:aws:ssm:$AWS_REGION:$AWS_ACCOUNT_ID:parameter/smartcloudops/gemini_api_key"}
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/$PROJECT_NAME",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "ecs"
                }
            },
            "healthCheck": {
                "command": ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"],
                "interval": 30,
                "timeout": 5,
                "retries": 3,
                "startPeriod": 60
            }
        }
    ]
}
EOF
    
    # Register task definition
    aws ecs register-task-definition --cli-input-json file://task-definition.json --region $AWS_REGION
    log "Task definition created successfully!"
}

# Create ECS service
create_ecs_service() {
    log "Creating ECS service..."
    
    # Check if service exists
    if aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION --query 'services[0].status' --output text 2>/dev/null | grep -q "ACTIVE"; then
        log "ECS service $SERVICE_NAME already exists. Updating..."
        aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --task-definition $TASK_DEFINITION_NAME --region $AWS_REGION
    else
        # Create service
        aws ecs create-service \
            --cluster $CLUSTER_NAME \
            --service-name $SERVICE_NAME \
            --task-definition $TASK_DEFINITION_NAME \
            --desired-count 2 \
            --launch-type FARGATE \
            --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SECURITY_GROUP_IDS],assignPublicIp=ENABLED}" \
            --region $AWS_REGION
    fi
    
    log "ECS service created/updated successfully!"
}

# Create CloudWatch log group
create_log_group() {
    log "Creating CloudWatch log group..."
    
    aws logs create-log-group --log-group-name "/ecs/$PROJECT_NAME" --region $AWS_REGION 2>/dev/null || {
        log "Log group already exists."
    }
}

# Store secrets in AWS Systems Manager Parameter Store
store_secrets() {
    log "Storing secrets in AWS Systems Manager Parameter Store..."
    
    # Store database URL
    aws ssm put-parameter \
        --name "/smartcloudops/database_url" \
        --value "$DATABASE_URL" \
        --type "SecureString" \
        --region $AWS_REGION \
        --overwrite
    
    # Store OpenAI API key
    if [ ! -z "$OPENAI_API_KEY" ]; then
        aws ssm put-parameter \
            --name "/smartcloudops/openai_api_key" \
            --value "$OPENAI_API_KEY" \
            --type "SecureString" \
            --region $AWS_REGION \
            --overwrite
    fi
    
    # Store Gemini API key
    if [ ! -z "$GEMINI_API_KEY" ]; then
        aws ssm put-parameter \
            --name "/smartcloudops/gemini_api_key" \
            --value "$GEMINI_API_KEY" \
            --type "SecureString" \
            --region $AWS_REGION \
            --overwrite
    fi
    
    log "Secrets stored successfully!"
}

# Main deployment function
main() {
    log "Starting SmartCloudOps AI deployment to AWS..."
    
    # Check prerequisites
    check_prerequisites
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --region $AWS_REGION)
    log "AWS Account ID: $AWS_ACCOUNT_ID"
    
    # Store secrets
    store_secrets
    
    # Build and push Docker image
    build_and_push_image
    
    # Create ECS cluster
    create_ecs_cluster
    
    # Create CloudWatch log group
    create_log_group
    
    # Create task definition
    create_task_definition
    
    # Create ECS service
    create_ecs_service
    
    log "Deployment completed successfully!"
    log "Your SmartCloudOps AI application is now running on AWS ECS!"
    log "Service URL: http://your-load-balancer-url"
    log "Grafana Dashboard: http://your-load-balancer-url:3000"
    log "Prometheus Metrics: http://your-load-balancer-url:9090"
}

# Check if required environment variables are set
if [ -z "$SUBNET_IDS" ] || [ -z "$SECURITY_GROUP_IDS" ]; then
    error "Please set the following environment variables:"
    error "  SUBNET_IDS - Comma-separated list of subnet IDs"
    error "  SECURITY_GROUP_IDS - Comma-separated list of security group IDs"
    error "  DATABASE_URL - PostgreSQL database connection string"
    error "  OPENAI_API_KEY - OpenAI API key (optional)"
    error "  GEMINI_API_KEY - Gemini API key (optional)"
fi

# Run main function
main "$@"
