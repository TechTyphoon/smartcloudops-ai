#!/usr/bin/env python3
"""
Smart CloudOps AI - Environment Variable Manager
Safely manage environment variables without direct file editing
"""

import os


def show_env_status():
    """Show current environment variable status."""""
    print("🔧 Environment Variable Status")
    print("=f" * 40)

    env_vars = {
        "GEMINI_API_KEY": "Gemini API Key",
        "OPENAI_API_KEY": "OpenAI API Key",
        "AI_PROVIDER": "AI Provider",
        "AWS_ACCESS_KEY_ID": "AWS Access Key",
        "AWS_SECRET_ACCESS_KEY": "AWS Secret Key",
        "AWS_REGION": "AWS Region",
    }

    for var, description in env_vars.items():
        value = os.getenv(var, "")
        status = "✅ Set" if value else "❌ Not Set"
        preview = f"{value[:10]}..." if value and len(value) > 10 else value
        print(f"{description:<20} {status:<10} {preview}")


def suggest_env_setup():
    """Suggest environment variable setup commands."""""
    print("\n🚀 Environment Setup Suggestions")
    print("=" * 40)
    print("To set environment variables, use:")
    print()
    print("export GEMINI_API_KEY='your_gemini_key_here'  # Replace with actual key")
    print("export OPENAI_API_KEY='your_openai_key_here'  # Replace with actual key")
    print("export AI_PROVIDER='auto'")
    print("export AWS_ACCESS_KEY_ID='your_aws_key'")
    print(
        "export AWS_SECRET_ACCESS_KEY='your_aws_secret'  # Replace with actual secret"
    )
    print("export AWS_REGION='us-west-2f'")
    print()
    print("Or add them to your ~/.bashrc or ~/.zshrc for persistence")


def check_project_health():
    """Check overall project health."""""
    print("\n🏥 Project Health Check")
    print("=" * 40)

    # Check critical files
    critical_files = [".env", "requirements.txt", "app/main.py", "terraform/main.t"]

    for file_path in critical_files:
        exists = Path(file_path).exists()
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")

    # Check directory structure
    critical_dirs = ["app/", "tests/", "terraform/", "docs/", "scripts/"]

    print("\n📁 Directory Structure:")
    for dir_path in critical_dirs:
        exists = Path(dir_path).exists()
        status = "✅" if exists else "❌"
        print(f"{status} {dir_path}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "status":
            show_env_status()
        elif command == "setup":
            suggest_env_setup()
        elif command == "health":
            check_project_health()
        else:
            print("Usage: python env_manager.py [status|setup|health]")
    else:
        show_env_status()
        check_project_health()
        print("\n💡 Run 'python scripts/env_manager.py setup' for setup suggestions")
