#!/bin/bash

# SmartCloudOps AI - Infrastructure Setup Script
# Sets up complete infrastructure with Terraform, Kubernetes, and MLOps

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="smartcloudops-ai"
ENVIRONMENT="${ENVIRONMENT:-production}"
AWS_REGION="${AWS_REGION:-us-west-2}"
KUBERNETES_VERSION="1.28"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

# Setup S3 backend for Terraform
setup_terraform_backend() {
    log_info "Setting up Terraform S3 backend..."
    
    BUCKET_NAME="${PROJECT_NAME}-terraform-state-${ENVIRONMENT}"
    DYNAMODB_TABLE="${PROJECT_NAME}-terraform-locks-${ENVIRONMENT}"
    
    # Create S3 bucket if it doesn't exist
    if ! aws s3 ls "s3://${BUCKET_NAME}" &> /dev/null; then
        log_info "Creating S3 bucket: ${BUCKET_NAME}"
        aws s3 mb "s3://${BUCKET_NAME}" --region "${AWS_REGION}"
        
        # Enable versioning
        aws s3api put-bucket-versioning \
            --bucket "${BUCKET_NAME}" \
            --versioning-configuration Status=Enabled
        
        # Enable encryption
        aws s3api put-bucket-encryption \
            --bucket "${BUCKET_NAME}" \
            --server-side-encryption-configuration '{
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }'
        
        # Block public access
        aws s3api put-public-access-block \
            --bucket "${BUCKET_NAME}" \
            --public-access-block-configuration \
            BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
    fi
    
    # Create DynamoDB table for state locking
    if ! aws dynamodb describe-table --table-name "${DYNAMODB_TABLE}" &> /dev/null; then
        log_info "Creating DynamoDB table: ${DYNAMODB_TABLE}"
        aws dynamodb create-table \
            --table-name "${DYNAMODB_TABLE}" \
            --attribute-definitions AttributeName=LockID,AttributeType=S \
            --key-schema AttributeName=LockID,KeyType=HASH \
            --billing-mode PAY_PER_REQUEST \
            --region "${AWS_REGION}"
        
        # Wait for table to be active
        aws dynamodb wait table-exists --table-name "${DYNAMODB_TABLE}"
    fi
    
    log_success "Terraform backend setup completed"
}

# Initialize Terraform
init_terraform() {
    log_info "Initializing Terraform..."
    
    cd terraform
    
    # Initialize with backend configuration
    terraform init \
        -backend-config="bucket=${PROJECT_NAME}-terraform-state-${ENVIRONMENT}" \
        -backend-config="key=terraform.tfstate" \
        -backend-config="region=${AWS_REGION}" \
        -backend-config="dynamodb_table=${PROJECT_NAME}-terraform-locks-${ENVIRONMENT}" \
        -backend-config="encrypt=true"
    
    # Validate configuration
    terraform validate
    
    log_success "Terraform initialized successfully"
}

# Deploy infrastructure
deploy_infrastructure() {
    log_info "Deploying infrastructure..."
    
    cd terraform
    
    # Plan deployment
    log_info "Creating Terraform plan..."
    terraform plan \
        -var="environment=${ENVIRONMENT}" \
        -var="aws_region=${AWS_REGION}" \
        -out=tfplan
    
    # Apply deployment
    log_info "Applying Terraform configuration..."
    terraform apply tfplan
    
    # Get outputs
    log_info "Getting infrastructure outputs..."
    terraform output -json > ../infrastructure-outputs.json
    
    log_success "Infrastructure deployment completed"
}

# Setup Kubernetes cluster
setup_kubernetes() {
    log_info "Setting up Kubernetes cluster..."
    
    # Get cluster info from Terraform outputs
    CLUSTER_NAME=$(jq -r '.eks_cluster_name.value' infrastructure-outputs.json)
    
    if [ -z "$CLUSTER_NAME" ] || [ "$CLUSTER_NAME" = "null" ]; then
        log_error "Could not get EKS cluster name from Terraform outputs"
        exit 1
    fi
    
    # Update kubeconfig
    aws eks update-kubeconfig --region "${AWS_REGION}" --name "${CLUSTER_NAME}"
    
    # Verify cluster access
    kubectl cluster-info
    
    log_success "Kubernetes cluster setup completed"
}

# Install ArgoCD
install_argocd() {
    log_info "Installing ArgoCD..."
    
    # Create namespace
    kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
    
    # Install ArgoCD
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
    
    # Wait for ArgoCD to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd
    
    # Get initial admin password
    ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
    
    # Get ArgoCD server URL
    ARGOCD_SERVER=$(kubectl get svc argocd-server -n argocd -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    
    log_success "ArgoCD installed successfully"
    log_info "ArgoCD Server: https://${ARGOCD_SERVER}"
    log_info "Username: admin"
    log_info "Password: ${ARGOCD_PASSWORD}"
    
    # Save credentials
    echo "ARGOCD_SERVER=https://${ARGOCD_SERVER}" > argocd-credentials.env
    echo "ARGOCD_PASSWORD=${ARGOCD_PASSWORD}" >> argocd-credentials.env
}

# Setup MLflow
setup_mlflow() {
    log_info "Setting up MLflow..."
    
    # Create namespace
    kubectl create namespace mlflow --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy MLflow
    kubectl apply -f k8s/mlflow-deployment.yaml
    
    # Wait for MLflow to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/mlflow -n mlflow
    
    # Get MLflow URL
    MLFLOW_URL=$(kubectl get svc mlflow -n mlflow -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    
    log_success "MLflow setup completed"
    log_info "MLflow URL: http://${MLFLOW_URL}"
    
    # Save MLflow URL
    echo "MLFLOW_TRACKING_URI=http://${MLFLOW_URL}" > mlflow-credentials.env
}

# Deploy applications
deploy_applications() {
    log_info "Deploying applications via ArgoCD..."
    
    # Apply ArgoCD applications
    kubectl apply -f k8s/argocd-app.yaml
    
    # Wait for applications to sync
    log_info "Waiting for applications to sync..."
    kubectl wait --for=condition=available --timeout=600s application/smartcloudops-ai -n argocd
    kubectl wait --for=condition=available --timeout=600s application/smartcloudops-ml-pipeline -n argocd
    kubectl wait --for=condition=available --timeout=600s application/smartcloudops-monitoring -n argocd
    
    log_success "Applications deployed successfully"
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring stack..."
    
    # Deploy Prometheus and Grafana
    kubectl apply -f k8s/monitoring.yaml
    
    # Wait for monitoring to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/prometheus -n monitoring
    kubectl wait --for=condition=available --timeout=300s deployment/grafana -n monitoring
    
    # Get monitoring URLs
    PROMETHEUS_URL=$(kubectl get svc prometheus -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    GRAFANA_URL=$(kubectl get svc grafana -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    
    log_success "Monitoring setup completed"
    log_info "Prometheus URL: http://${PROMETHEUS_URL}"
    log_info "Grafana URL: http://${GRAFANA_URL}"
}

# Setup security
setup_security() {
    log_info "Setting up security configurations..."
    
    # Apply network policies
    kubectl apply -f k8s/network-policies.yaml
    
    # Apply security contexts (already in deployment files)
    log_info "Security contexts configured in deployment manifests"
    
    # Setup RBAC
    kubectl apply -f k8s/rbac/
    
    log_success "Security setup completed"
}

# Generate deployment summary
generate_summary() {
    log_info "Generating deployment summary..."
    
    cat > deployment-summary.md << EOF
# SmartCloudOps AI - Infrastructure Deployment Summary

## Environment: ${ENVIRONMENT}
## Region: ${AWS_REGION}
## Deployment Date: $(date)

## Services Deployed:

### Infrastructure
- EKS Cluster: $(jq -r '.eks_cluster_name.value' infrastructure-outputs.json)
- VPC: $(jq -r '.vpc_id.value' infrastructure-outputs.json)
- RDS Database: $(jq -r '.rds_endpoint.value' infrastructure-outputs.json)

### Applications
- SmartCloudOps AI: Deployed via ArgoCD
- ML Pipeline: Deployed via ArgoCD
- Monitoring Stack: Deployed via ArgoCD

### MLOps
- MLflow Tracking Server: http://$(kubectl get svc mlflow -n mlflow -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
- ArgoCD: https://$(kubectl get svc argocd-server -n argocd -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

### Monitoring
- Prometheus: http://$(kubectl get svc prometheus -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
- Grafana: http://$(kubectl get svc grafana -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

## Next Steps:
1. Configure GitHub secrets for CI/CD
2. Set up monitoring dashboards
3. Configure alerting rules
4. Test ML pipeline
5. Set up backup and disaster recovery

## Credentials:
- ArgoCD credentials saved in: argocd-credentials.env
- MLflow credentials saved in: mlflow-credentials.env
EOF
    
    log_success "Deployment summary generated: deployment-summary.md"
}

# Main execution
main() {
    log_info "Starting SmartCloudOps AI infrastructure setup..."
    
    check_prerequisites
    setup_terraform_backend
    init_terraform
    deploy_infrastructure
    setup_kubernetes
    install_argocd
    setup_mlflow
    deploy_applications
    setup_monitoring
    setup_security
    generate_summary
    
    log_success "Infrastructure setup completed successfully!"
    log_info "Check deployment-summary.md for details"
}

# Run main function
main "$@"
