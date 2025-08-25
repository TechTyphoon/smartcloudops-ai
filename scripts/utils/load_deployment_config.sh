#!/bin/bash
# SmartCloudOps AI - Deployment Configuration Loader
# Loads deployment configuration from environment files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default configuration file paths
CONFIG_FILES=(
    ".env.deployment"
    "configs/deployment.env"
    ".env"
)

# Load configuration from file
load_config() {
    local config_file="$1"
    
    if [[ -f "$config_file" ]]; then
        print_status "Loading configuration from $config_file"
        
        # Export all variables from the file
        while IFS= read -r line; do
            # Skip comments and empty lines
            if [[ "$line" =~ ^[[:space:]]*# ]] || [[ -z "$line" ]]; then
                continue
            fi
            
            # Export variable if it's a valid assignment
            if [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
                export "$line"
            fi
        done < "$config_file"
        
        print_success "Configuration loaded from $config_file"
        return 0
    fi
    
    return 1
}

# Load configuration from multiple possible files
load_deployment_config() {
    local config_loaded=false
    
    for config_file in "${CONFIG_FILES[@]}"; do
        if load_config "$config_file"; then
            config_loaded=true
            break
        fi
    done
    
    if [[ "$config_loaded" == false ]]; then
        print_warning "No configuration file found. Using default values."
        print_status "Create .env.deployment or configs/deployment.env for custom configuration."
    fi
}

# Validate required configuration
validate_config() {
    local required_vars=(
        "APP_SERVER"
        "MONITORING_SERVER"
        "KEY_FILE"
        "IMAGE_NAME"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        print_error "Missing required configuration variables:"
        for var in "${missing_vars[@]}"; do
            print_error "  - $var"
        done
        return 1
    fi
    
    print_success "Configuration validation passed"
    return 0
}

# Display current configuration
show_config() {
    print_status "Current deployment configuration:"
    echo "  APP_SERVER: $APP_SERVER"
    echo "  MONITORING_SERVER: $MONITORING_SERVER"
    echo "  KEY_FILE: $KEY_FILE"
    echo "  IMAGE_NAME: $IMAGE_NAME"
    echo "  AWS_REGION: $AWS_REGION"
    echo "  ENVIRONMENT: $ENVIRONMENT"
    echo "  APP_PORT: $APP_PORT"
    echo "  GRAFANA_PORT: $GRAFANA_PORT"
    echo "  PROMETHEUS_PORT: $PROMETHEUS_PORT"
    echo "  NODE_EXPORTER_PORT: $NODE_EXPORTER_PORT"
}

# Main function
main() {
    print_status "🔧 Loading SmartCloudOps AI deployment configuration"
    
    # Load configuration
    load_deployment_config
    
    # Validate configuration
    if ! validate_config; then
        exit 1
    fi
    
    # Show configuration
    show_config
    
    print_success "✅ Configuration loaded successfully"
}

# If script is sourced, just load config
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    load_deployment_config
    validate_config
else
    main "$@"
fi
