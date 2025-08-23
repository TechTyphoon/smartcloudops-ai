# Makefile for Smart CloudOps AI
# One-command local CI replication

.PHONY: help install install-dev clean lint format test test-unit test-integration security build docker-build ci all

# Default Python interpreter
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest

# Virtual environment
VENV := .venv
VENV_BIN := $(VENV)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip

help: ## Show this help message
	@echo "Smart CloudOps AI - Development Commands"
	@echo "========================================"
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development Setup

install: ## Install production dependencies
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements-production.txt

install-dev: ## Install development dependencies
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements-production.txt
	$(PIP) install -r requirements-dev.txt

venv: ## Create virtual environment
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip setuptools wheel

setup: venv install-dev ## Complete development setup

##@ Code Quality

format: ## Format code with black and isort
	@echo "🎨 Formatting code..."
	$(PYTHON) -m black .
	$(PYTHON) -m isort .

lint: ## Run all linters
	@echo "🔍 Running linters..."
	$(PYTHON) -m flake8 .
	$(PYTHON) -m black --check .
	$(PYTHON) -m isort --check-only .
	@echo "✅ Linting complete"

lint-fix: format ## Fix linting issues

##@ Testing

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	$(PYTEST) -m "unit" --maxfail=1

test-integration: ## Run integration tests only
	@echo "🔗 Running integration tests..."
	$(PYTEST) -m "integration" --maxfail=1

test: ## Run all tests with coverage
	@echo "🧪 Running all tests..."
	$(PYTEST) --maxfail=3 --tb=short

test-backend: ## Run backend tests with coverage
	@echo "🧪 Running backend tests..."
	$(PYTEST) tests/backend/ --cov=app --cov-report=xml --cov-report=html --maxfail=1

test-frontend: ## Run frontend lint and type checks
	@echo "🎨 Running frontend tests..."
	cd smartcloudops-ai && npm run lint && npm run typecheck

test-e2e: ## Run E2E tests with Playwright
	@echo "🌐 Running E2E tests..."
	cd smartcloudops-ai && npx playwright test --reporter=line

test-all: ## Run full test suite (backend + frontend + e2e)
	@echo "🚀 Running full test suite..."
	./scripts/test-local.sh

test-fast: ## Run tests in parallel (fast)
	@echo "⚡ Running tests in parallel..."
	$(PYTEST) -n auto --maxfail=1

test-watch: ## Run tests in watch mode
	@echo "👀 Running tests in watch mode..."
	$(PYTEST) -f

##@ Security

security: ## Run security scans
	@echo "🔒 Running security scans..."
	$(PYTHON) -m bandit -r . -f json -o bandit_report.json
	$(PYTHON) -m safety check
	@echo "✅ Security scans complete"

##@ Build & Deploy

clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean ## Build distribution packages
	@echo "📦 Building packages..."
	$(PYTHON) -m build

docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -f Dockerfile.production -t smartcloudops-ai:latest .

##@ CI/CD Replication

ci: clean install-dev lint security test ## 🚀 MAIN CI COMMAND - Run complete CI pipeline locally
	@echo ""
	@echo "🎉 CI Pipeline completed successfully!"
	@echo "✅ All checks passed - ready for production"

ci-fast: clean install-dev lint test-fast ## Fast CI pipeline (parallel tests)
	@echo ""
	@echo "⚡ Fast CI Pipeline completed!"

pre-commit: format lint test-unit ## Pre-commit checks (quick)
	@echo "✅ Pre-commit checks passed"

##@ Docker Development

docker-dev: ## Start development environment with Docker
	docker-compose -f docker-compose.yml up --build

docker-prod: ## Start production environment with Docker
	docker-compose -f docker-compose.production.yml up --build

docker-test: ## Run tests in Docker
	docker-compose -f docker-compose.yml run --rm app make test

##@ Utilities

logs: ## Show application logs
	tail -f logs/*.log 2>/dev/null || echo "No logs found"

install-hooks: ## Install pre-commit hooks
	$(PYTHON) -m pre_commit install

check-deps: ## Check for dependency vulnerabilities
	$(PYTHON) -m safety check
	$(PYTHON) -m pip-audit

update-deps: ## Update dependencies
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install --upgrade -r requirements-production.txt -r requirements-dev.txt

##@ Information

status: ## Show project status
	@echo "Smart CloudOps AI - Project Status"
	@echo "=================================="
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"
	@echo "Working Directory: $(shell pwd)"
	@echo "Git Branch: $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'Not a git repo')"
	@echo "Git Status: $(shell git status --porcelain 2>/dev/null | wc -l || echo '0') uncommitted changes"

##@ Special Targets

all: ci docker-build ## Run everything (CI + Docker build)

# Default target
.DEFAULT_GOAL := help
