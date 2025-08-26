#!/bin/bash
# SmartCloudOps AI - Infrastructure Deployment Script
# Phase 3 Week 5: Infrastructure as Code (IaC) - Deployment Automation

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TERRAFORM_DIR="${PROJECT_ROOT}/infrastructure/terraform"
KUBERNETES_DIR="${PROJECT_ROOT}/infrastructure/kubernetes"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Help function
show_help() {
    cat << EOF
SmartCloudOps AI Infrastructure Deployment Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    plan                    Run Terraform plan
    apply                   Apply Terraform configuration
    destroy                 Destroy infrastructure
    kubernetes              Deploy Kubernetes manifests
    all                     Deploy complete infrastructure (Terraform + Kubernetes)
    validate                Validate configurations
    status                  Show deployment status

Options:
    -e, --environment       Environment (dev, staging, production) [default: production]
    -r, --region           AWS region [default: us-west-2]
    -v, --verbose          Verbose output
    -h, --help             Show this help message

Examples:
    $0 plan -e production
    $0 apply -e staging -r us-east-1
    $0 kubernetes -e production
    $0 all -e production -v

EOF
}

# Default values
ENVIRONMENT="production"
AWS_REGION="us-west-2"
VERBOSE=false
COMMAND=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        plan|apply|destroy|kubernetes|all|validate|status)
            COMMAND="$1"
            shift
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate command
if [[ -z "$COMMAND" ]]; then
    log_error "No command specified"
    show_help
    exit 1
fi

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    log_error "Invalid environment: $ENVIRONMENT"
    exit 1
fi

# Set verbose mode
if [[ "$VERBOSE" == "true" ]]; then
    set -x
fi

# Prerequisites check
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check required tools
    local tools=("terraform" "kubectl" "aws" "helm")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is not installed or not in PATH"
            exit 1
        fi
    done
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured"
        exit 1
    fi
    
    # Check Terraform version
    local tf_version=$(terraform version -json | jq -r '.terraform_version')
    log_info "Terraform version: $tf_version"
    
    # Check kubectl context
    local current_context=$(kubectl config current-context 2>/dev/null || echo "none")
    log_info "Kubectl context: $current_context"
    
    log_success "Prerequisites check completed"
}

# Initialize Terraform
terraform_init() {
    log_info "Initializing Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    # Create backend configuration
    cat > backend.hcl << EOF
bucket         = "smartcloudops-terraform-state-${ENVIRONMENT}"
key            = "smartcloudops/${ENVIRONMENT}/terraform.tfstate"
region         = "${AWS_REGION}"
encrypt        = true
dynamodb_table = "smartcloudops-terraform-locks-${ENVIRONMENT}"
EOF
    
    # Initialize Terraform
    terraform init -backend-config=backend.hcl
    
    log_success "Terraform initialized"
}

# Terraform plan
terraform_plan() {
    log_info "Running Terraform plan..."
    
    cd "$TERRAFORM_DIR"
    
    # Create terraform.tfvars
    cat > terraform.tfvars << EOF
environment = "${ENVIRONMENT}"
aws_region  = "${AWS_REGION}"

# Environment-specific overrides
$(case "$ENVIRONMENT" in
    dev)
        echo 'eks_node_groups = {
          general = {
            instance_types = ["t3.small"]
            min_size      = 1
            max_size      = 3
            desired_size  = 1
            disk_size     = 20
            ami_type      = "AL2_x86_64"
            capacity_type = "SPOT"
            labels = { role = "general" }
            taints = []
          }
        }
        rds_instance_class = "db.t3.micro"
        redis_node_type   = "cache.t3.micro"'
        ;;
    staging)
        echo 'eks_node_groups = {
          general = {
            instance_types = ["t3.medium"]
            min_size      = 1
            max_size      = 5
            desired_size  = 2
            disk_size     = 30
            ami_type      = "AL2_x86_64"
            capacity_type = "ON_DEMAND"
            labels = { role = "general" }
            taints = []
          }
        }
        rds_instance_class = "db.t3.small"
        redis_node_type   = "cache.t3.small"'
        ;;
    production)
        echo '# Production uses default values from variables.tf'
        ;;
esac)
EOF
    
    # Run plan
    terraform plan -var-file=terraform.tfvars -out=tfplan
    
    log_success "Terraform plan completed"
}

# Terraform apply
terraform_apply() {
    log_info "Applying Terraform configuration..."
    
    cd "$TERRAFORM_DIR"
    
    # Apply the plan
    terraform apply tfplan
    
    # Save outputs
    terraform output -json > outputs.json
    
    log_success "Terraform apply completed"
}

# Deploy Kubernetes manifests
deploy_kubernetes() {
    log_info "Deploying Kubernetes manifests..."
    
    # Get EKS cluster info from Terraform outputs
    if [[ -f "$TERRAFORM_DIR/outputs.json" ]]; then
        local cluster_name=$(jq -r '.cluster_name.value' "$TERRAFORM_DIR/outputs.json")
        local cluster_endpoint=$(jq -r '.cluster_endpoint.value' "$TERRAFORM_DIR/outputs.json")
        
        # Update kubeconfig
        aws eks update-kubeconfig --region "$AWS_REGION" --name "$cluster_name"
        
        log_info "Connected to EKS cluster: $cluster_name"
    else
        log_warning "Terraform outputs not found, assuming kubectl is already configured"
    fi
    
    # Apply Kubernetes manifests in order
    local manifests=(
        "namespace.yaml"
        "configmap.yaml"
        "secrets.yaml"
        "service.yaml"
        "deployment.yaml"
        "ingress.yaml"
        "autoscaling.yaml"
    )
    
    for manifest in "${manifests[@]}"; do
        local manifest_path="$KUBERNETES_DIR/$manifest"
        if [[ -f "$manifest_path" ]]; then
            log_info "Applying $manifest..."
            kubectl apply -f "$manifest_path"
        else
            log_warning "Manifest not found: $manifest"
        fi
    done
    
    # Wait for deployments to be ready
    log_info "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/smartcloudops-api -n smartcloudops
    kubectl wait --for=condition=available --timeout=300s deployment/smartcloudops-worker -n smartcloudops
    
    log_success "Kubernetes deployment completed"
}

# Validate configurations
validate_configs() {
    log_info "Validating configurations..."
    
    # Validate Terraform
    cd "$TERRAFORM_DIR"
    terraform validate
    terraform fmt -check=true
    
    # Validate Kubernetes manifests
    for manifest in "$KUBERNETES_DIR"/*.yaml; do
        if [[ -f "$manifest" ]]; then
            kubectl apply --dry-run=client --validate=true -f "$manifest" > /dev/null
        fi
    done
    
    log_success "Configuration validation completed"
}

# Show deployment status
show_status() {
    log_info "Deployment status:"
    
    # Terraform status
    if [[ -f "$TERRAFORM_DIR/terraform.tfstate" ]]; then
        cd "$TERRAFORM_DIR"
        log_info "Terraform state:"
        terraform show -json | jq -r '.values.root_module.resources[] | select(.type == "aws_eks_cluster") | .values.name'
    fi
    
    # Kubernetes status
    if kubectl cluster-info &> /dev/null; then
        log_info "Kubernetes status:"
        kubectl get nodes -o wide
        kubectl get pods -n smartcloudops -o wide
        kubectl get services -n smartcloudops
        kubectl get ingress -n smartcloudops
    fi
}

# Cleanup function
cleanup() {
    if [[ "$VERBOSE" == "true" ]]; then
        set +x
    fi
}

trap cleanup EXIT

# Main execution
main() {
    log_info "Starting SmartCloudOps AI infrastructure deployment"
    log_info "Environment: $ENVIRONMENT"
    log_info "Region: $AWS_REGION"
    log_info "Command: $COMMAND"
    
    check_prerequisites
    
    case "$COMMAND" in
        plan)
            terraform_init
            terraform_plan
            ;;
        apply)
            terraform_init
            terraform_plan
            terraform_apply
            ;;
        destroy)
            terraform_init
            cd "$TERRAFORM_DIR"
            terraform destroy -var-file=terraform.tfvars
            ;;
        kubernetes)
            deploy_kubernetes
            ;;
        all)
            terraform_init
            terraform_plan
            terraform_apply
            deploy_kubernetes
            show_status
            ;;
        validate)
            validate_configs
            ;;
        status)
            show_status
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            exit 1
            ;;
    esac
    
    log_success "Operation completed successfully"
}

# Run main function
main "$@"
