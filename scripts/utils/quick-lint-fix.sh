#!/bin/bash
# Quick linting fixes for common issues
# This addresses the issues caught by pre-commit hooks

echo "=== Quick Linting Fixes ==="

# Activate virtual environment
source smartcloudops_env/bin/activate

echo "1. Installing development tools..."
pip install -q black isort flake8 autoflake

echo "2. Removing unused imports..."
autoflake --remove-all-unused-imports --recursive --in-place app/ || true

echo "3. Fixing import order..."
isort app/ --profile black || true

echo "4. Formatting code..."
black app/ || true

echo "5. Running final check..."
echo "Checking app/ directory only (ignoring scripts/examples for now):"
flake8 app/ --count --statistics --max-line-length=88 --max-complexity=10 || true

echo "✅ Quick fixes applied to app/ directory"
echo "Note: Scripts and examples may still have issues (addressed in CI/CD)"
