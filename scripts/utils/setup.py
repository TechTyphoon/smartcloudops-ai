#!/usr/bin/env python3
"""
Smart CloudOps AI - Setup Script
This script helps set up the development environment for the Smart CloudOps AI project.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def run_command(command, description=""):
    """Run a shell command and handle errors."""
    import shlex

    print(f"🔧 {description}")
    try:
        # Parse command safely - split shell command into list
        if isinstance(command, str):
            cmd_list = shlex.split(command)
        else:
            cmd_list = command

        result = subprocess.run(
            cmd_list,
            shell=False,  # Security fix: Never use shell=True
            capture_output=True,
            text=True,
            timeout=300,  # Add timeout for security
        )
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {description} - Command timed out")
        return False
    except Exception as e:
        print(f"❌ {description} - Error: {str(e)}")
        return False


def check_prerequisites():
    """Check if required tools are installed."""
    print("🔍 Checking prerequisites...f")

    required_tools = {
        "python3": "python3 --version",
        "docker": "docker --version",
        "terraform": "terraform --version",
        "aws": "aws --version",
        "git": "git --version",
    }

    missing_tools = []

    for tool, command in required_tools.items():
        if run_command(command, f"Checking {tool}"):
            continue
        else:
            missing_tools.append(tool)

    if missing_tools:
        print(f"❌ Missing tools: {', '.join(missing_tools)}")
        print("Please install the missing tools before continuing.")
        return False

    print("✅ All prerequisites are installed!")
    return True


def setup_python_environment():
    """Set up Python virtual environment and install dependencies."""
    print("\n🐍 Setting up Python environment...")

    # Create virtual environment
    if not run_command("python3 -m venv venv", "Creating virtual environment"):
        return False

    # Determine activation script based on OS
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
        pip_command = "venv\\Scripts\\pip"
    else:
        activate_script = "source venv/bin/activate"
        pip_command = "venv/bin/pip"

    # Install dependencies
    if not run_command(f"{pip_command} install --upgrade pip", "Upgrading pip"):
        return False

    if not run_command(
        f"{pip_command} install -r requirements.txt", "Installing Python dependencies"
    ):
        return False

    print("✅ Python environment setup complete!")
    print(f"💡 To activate the environment, run: {activate_script}")
    return True


def setup_git_hooks():
    """Set up git hooks for code quality."""
    print("\n📝 Setting up git hooks...")

    hooks_dir = Path(".git/hooks")
    if not hooks_dir.exists():
        print("❌ .git directory not found. Please initialize git repository first.")
        return False

    pre_commit_hook = hooks_dir / "pre-commit"

    hook_content = """#!/bin/bash
# Pre-commit hook for Smart CloudOps AI

echo "🔍 Running pre-commit checks..."

# Check Python code formatting
if command -v black &> /dev/null; then
    echo "🎨 Checking code formatting with black..."
    black --check app/ scripts/ || exit 1
fi

# Check import sorting
if command -v isort &> /dev/null; then
    echo "📦 Checking import sorting with isort..."
    isort --check-only app/ scripts/ || exit 1
fi

# Run linting
if command -v flake8 &> /dev/null; then
    echo "🔍 Running flake8 linting..."
    flake8 app/ scripts/ || exit 1
fi

echo "✅ Pre-commit checks passed!"
"""

    try:
        with open(pre_commit_hook, "w") as f:
            f.write(hook_content)
        os.chmod(pre_commit_hook, 0o755)
        print("✅ Git hooks setup complete!")
        return True
    except Exception as e:
        print(f"❌ Failed to setup git hooks: {str(e)}")
        return False


def create_env_file():
    """Create a sample .env file."""
    print("\n⚙️ Creating sample .env file...")

    env_content = """# Smart CloudOps AI Environment Variables
# Copy this file to .env and update with your actual values

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# AWS Configuration
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here

# Prometheus Configuration
PROMETHEUS_URL=http://localhost:9090

# Grafana Configuration
GRAFANA_URL=http://localhost:3001
GRAFANA_USERNAME=admin
GRAFANA_PASSWORD=admin

# Application Configuration
LOG_LEVEL=INFO
"""

    try:
        if not os.path.exists(".env.example"):
            with open(".env.example", "w") as f:
                f.write(env_content)
            print("✅ Created .env.example file!")
            print("💡 Copy .env.example to .env and update with your actual values")
        else:
            print("ℹ️  .env.example already exists")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env.example: {str(e)}")
        return False


def main():
    """Main setup function."""
    print("🚀 Smart CloudOps AI - Development Environment Setup")
    print("=" * 50)

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Setup Python environment
    if not setup_python_environment():
        print("❌ Failed to setup Python environment")
        sys.exit(1)

    # Setup git hooks
    if not setup_git_hooks():
        print("⚠️  Git hooks setup failed, but continuing...")

    # Create environment file
    if not create_env_file():
        print("⚠️  .env file creation failed, but continuing...")

    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment")
    print("2. Copy .env.example to .env and update with your values")
    print("3. Configure AWS credentials: aws configure")
    print("4. Start development: docker-compose up -d")
    print("\n📚 See README.md for detailed instructions")


if __name__ == "__main__":
    main()
