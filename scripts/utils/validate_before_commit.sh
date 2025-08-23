#!/bin/bash
echo "🔍 Pre-commit validation..."

# Check for sensitive data
if git diff --cached --name-only | grep -q "\.env$"; then
    echo "❌ ERROR: .env file in staging area!"
    exit 1
fi

# Check for large files
large_files=$(git diff --cached --name-only | xargs ls -la 2>/dev/null | awk '$5 > 10485760 {print $9}')
if [ ! -z "$large_files" ]; then
    echo "❌ ERROR: Large files detected: $large_files"
    exit 1
fi

# Basic syntax check for Python files
python_files=$(git diff --cached --name-only | grep "\.py$")
for file in $python_files; do
    if [ -f "$file" ]; then
        python3 -m py_compile "$file" || {
            echo "❌ ERROR: Syntax error in $file"
            exit 1
        }
    fi
done

echo "✅ Pre-commit validation passed!"
