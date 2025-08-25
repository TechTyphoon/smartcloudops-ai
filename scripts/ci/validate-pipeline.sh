#!/bin/bash
# CI/CD Pipeline Validation Script
# Validates GitHub Actions workflows and CI/CD setup

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WORKFLOWS_DIR=".github/workflows"
REQUIRED_WORKFLOWS=(
    "enhanced-pipeline.yml"
    "release-automation.yml"
    "performance-testing.yml"
    "cache-optimization.yml"
)

# Functions
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

check_workflow_exists() {
    local workflow="$1"
    if [[ -f "$WORKFLOWS_DIR/$workflow" ]]; then
        log_success "Workflow exists: $workflow"
        return 0
    else
        log_error "Missing workflow: $workflow"
        return 1
    fi
}

validate_yaml_syntax() {
    local workflow="$1"
    if command -v yamllint &> /dev/null; then
        if yamllint "$WORKFLOWS_DIR/$workflow" &> /dev/null; then
            log_success "YAML syntax valid: $workflow"
            return 0
        else
            log_error "YAML syntax error in: $workflow"
            yamllint "$WORKFLOWS_DIR/$workflow"
            return 1
        fi
    else
        log_warning "yamllint not installed, skipping YAML validation"
        return 0
    fi
}

check_workflow_permissions() {
    local workflow="$1"
    if grep -q "permissions:" "$WORKFLOWS_DIR/$workflow"; then
        log_success "Permissions defined in: $workflow"
        return 0
    else
        log_warning "No permissions defined in: $workflow"
        return 1
    fi
}

check_security_best_practices() {
    local workflow="$1"
    local issues=0
    
    # Check for hardcoded secrets
    if grep -q "password\|secret\|token" "$WORKFLOWS_DIR/$workflow" | grep -v "secrets\." | grep -v "inputs\." &> /dev/null; then
        log_warning "Potential hardcoded secrets in: $workflow"
        ((issues++))
    fi
    
    # Check for proper secret usage
    if grep -q '\${{ secrets\.' "$WORKFLOWS_DIR/$workflow"; then
        log_success "Proper secret usage found in: $workflow"
    fi
    
    # Check for timeout settings
    if grep -q "timeout-minutes:" "$WORKFLOWS_DIR/$workflow"; then
        log_success "Timeout configured in: $workflow"
    else
        log_warning "No timeout configured in: $workflow"
        ((issues++))
    fi
    
    return $issues
}

check_caching_strategy() {
    local workflow="$1"
    
    if grep -q "cache:" "$WORKFLOWS_DIR/$workflow" || grep -q "cache-from\|cache-to" "$WORKFLOWS_DIR/$workflow"; then
        log_success "Caching strategy found in: $workflow"
        return 0
    else
        log_warning "No caching strategy in: $workflow"
        return 1
    fi
}

validate_docker_builds() {
    local workflow="$1"
    
    if grep -q "docker/build-push-action" "$WORKFLOWS_DIR/$workflow"; then
        log_info "Docker build found in: $workflow"
        
        # Check for multi-platform builds
        if grep -q "platforms:" "$WORKFLOWS_DIR/$workflow"; then
            log_success "Multi-platform build configured"
        else
            log_warning "Single platform build only"
        fi
        
        # Check for security scanning
        if grep -q "trivy\|snyk\|anchore" "$WORKFLOWS_DIR/$workflow"; then
            log_success "Security scanning configured"
        else
            log_warning "No security scanning found"
        fi
    fi
}

check_job_dependencies() {
    local workflow="$1"
    
    if grep -q "needs:" "$WORKFLOWS_DIR/$workflow"; then
        log_success "Job dependencies configured in: $workflow"
        return 0
    else
        log_warning "No job dependencies in: $workflow"
        return 1
    fi
}

main() {
    log_info "Starting CI/CD Pipeline Validation"
    echo "=================================="
    
    local total_issues=0
    local workflow_count=0
    
    # Check if workflows directory exists
    if [[ ! -d "$WORKFLOWS_DIR" ]]; then
        log_error "Workflows directory not found: $WORKFLOWS_DIR"
        exit 1
    fi
    
    # Validate each required workflow
    for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
        echo ""
        log_info "Validating workflow: $workflow"
        echo "-----------------------------------"
        
        local workflow_issues=0
        
        # Check if workflow exists
        if ! check_workflow_exists "$workflow"; then
            ((workflow_issues++))
            ((total_issues++))
            continue
        fi
        
        ((workflow_count++))
        
        # Validate YAML syntax
        if ! validate_yaml_syntax "$workflow"; then
            ((workflow_issues++))
            ((total_issues++))
        fi
        
        # Check permissions
        if ! check_workflow_permissions "$workflow"; then
            ((workflow_issues++))
        fi
        
        # Security best practices
        check_security_best_practices "$workflow"
        security_issues=$?
        ((workflow_issues += security_issues))
        ((total_issues += security_issues))
        
        # Caching strategy
        if ! check_caching_strategy "$workflow"; then
            ((workflow_issues++))
        fi
        
        # Docker validation
        validate_docker_builds "$workflow"
        
        # Job dependencies
        if ! check_job_dependencies "$workflow"; then
            ((workflow_issues++))
        fi
        
        if [[ $workflow_issues -eq 0 ]]; then
            log_success "Workflow validation passed: $workflow"
        else
            log_warning "Workflow has $workflow_issues issues: $workflow"
        fi
    done
    
    # Additional checks
    echo ""
    log_info "Additional Validation Checks"
    echo "----------------------------"
    
    # Check for secrets documentation
    if [[ -f "docs/SECRETS.md" ]] || grep -r "secrets" docs/ &> /dev/null; then
        log_success "Secrets documentation found"
    else
        log_warning "No secrets documentation found"
        ((total_issues++))
    fi
    
    # Check for environment files
    if [[ -f ".env.example" ]]; then
        log_success "Environment example file found"
    else
        log_warning "No .env.example file found"
        ((total_issues++))
    fi
    
    # Check Dockerfile variations
    if [[ -f "Dockerfile.production" ]]; then
        log_success "Production Dockerfile found"
    else
        log_warning "No production Dockerfile found"
        ((total_issues++))
    fi
    
    # Check for CI scripts
    if [[ -d "scripts/ci" ]]; then
        log_success "CI scripts directory found"
    else
        log_warning "No CI scripts directory found"
    fi
    
    # Summary
    echo ""
    echo "======================================"
    log_info "Validation Summary"
    echo "======================================"
    echo "Workflows validated: $workflow_count/${#REQUIRED_WORKFLOWS[@]}"
    echo "Total issues found: $total_issues"
    
    if [[ $total_issues -eq 0 ]]; then
        log_success "🎉 All validations passed! CI/CD setup is excellent."
        exit 0
    elif [[ $total_issues -le 5 ]]; then
        log_warning "⚠️ Minor issues found. CI/CD setup is good but can be improved."
        exit 0
    else
        log_error "❌ Multiple issues found. CI/CD setup needs attention."
        exit 1
    fi
}

# Run main function
main "$@"
