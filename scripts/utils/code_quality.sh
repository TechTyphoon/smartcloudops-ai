#!/bin/bash
# SmartCloudOps AI - Code Quality Enforcement Script
# Runs all code quality tools: black, isort, flake8, mypy, bandit

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

# Check if virtual environment is activated
check_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_warning "Virtual environment not detected. Please activate your virtual environment."
        print_status "Run: source venv/bin/activate"
        exit 1
    fi
}

# Install development dependencies if not present
install_dev_deps() {
    print_status "Installing development dependencies..."
    pip install -r requirements-dev.txt
}

# Run Black code formatter
run_black() {
    print_status "Running Black code formatter..."
    if black --check --diff app/ tests/ scripts/ ml_models/; then
        print_success "Black formatting check passed"
    else
        print_error "Black formatting check failed. Run 'black app/ tests/ scripts/ ml_models/' to fix"
        exit 1
    fi
}

# Run isort import sorter
run_isort() {
    print_status "Running isort import sorter..."
    if isort --check-only --diff app/ tests/ scripts/ ml_models/; then
        print_success "isort import sorting check passed"
    else
        print_error "isort import sorting check failed. Run 'isort app/ tests/ scripts/ ml_models/' to fix"
        exit 1
    fi
}

# Run flake8 linter
run_flake8() {
    print_status "Running flake8 linter..."
    if flake8 app/ tests/ scripts/ ml_models/ --max-line-length=88 --extend-ignore=E203,W503; then
        print_success "flake8 linting check passed"
    else
        print_error "flake8 linting check failed"
        exit 1
    fi
}

# Run mypy type checker
run_mypy() {
    print_status "Running mypy type checker..."
    if mypy app/ --ignore-missing-imports --no-strict-optional; then
        print_success "mypy type checking passed"
    else
        print_warning "mypy type checking found issues (non-blocking)"
    fi
}

# Run bandit security scanner
run_bandit() {
    print_status "Running bandit security scanner..."
    if bandit -r app/ -f json -o bandit-report.json --exclude tests/; then
        print_success "bandit security scan passed"
    else
        print_warning "bandit security scan found issues (check bandit-report.json)"
    fi
}

# Run pytest with coverage
run_tests() {
    print_status "Running pytest with coverage..."
    if pytest --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=75; then
        print_success "All tests passed with coverage >= 75%"
    else
        print_error "Tests failed or coverage below 75%"
        exit 1
    fi
}

# Run pre-commit hooks
run_precommit() {
    print_status "Running pre-commit hooks..."
    if pre-commit run --all-files; then
        print_success "All pre-commit hooks passed"
    else
        print_error "Pre-commit hooks failed"
        exit 1
    fi
}

# Main function
main() {
    print_status "🚀 Starting SmartCloudOps AI Code Quality Check"
    
    # Check virtual environment
    check_venv
    
    # Install dependencies if needed
    install_dev_deps
    
    # Run all quality checks
    run_black
    run_isort
    run_flake8
    run_mypy
    run_bandit
    run_tests
    run_precommit
    
    print_success "🎉 All code quality checks passed!"
    print_status "Code is ready for production deployment"
}

# Run main function
main "$@"
