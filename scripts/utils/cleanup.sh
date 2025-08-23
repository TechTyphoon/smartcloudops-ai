#!/bin/bash
# Smart CloudOps AI - Repository Cleanup Script

echo "🧹 Smart CloudOps AI - Repository Cleanup"
echo "========================================"

# Remove Python cache files
echo "📁 Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null

# Remove test coverage files
echo "📊 Cleaning test coverage files..."
find . -name ".coverage*" -delete 2>/dev/null
find . -name "coverage.xml" -delete 2>/dev/null
find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null

# Remove temporary files
echo "🗑️  Cleaning temporary files..."
find . -name "*.tmp" -delete 2>/dev/null
find . -name "*.temp" -delete 2>/dev/null

# Remove IDE files
echo "💻 Cleaning IDE files..."
find . -name ".vscode" -type d -exec rm -rf {} + 2>/dev/null
find . -name ".idea" -type d -exec rm -rf {} + 2>/dev/null

# Show repository size
echo "📏 Repository size after cleanup:"
du -sh . 2>/dev/null

echo "✅ Cleanup completed!" 