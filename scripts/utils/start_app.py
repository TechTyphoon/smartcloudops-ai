#!/usr/bin/env python3
"""
Smart CloudOps AI - Application Startup Script
Helps users start the application with proper configuration
"""

import os
import sys
from pathlib import Path


def check_environment():
    """Check if environment is properly configured."""
    print("🔍 Checking environment configuration...")

    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Creating example configuration...")
        create_env_example()

    # Check AI provider API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    ai_provider = os.getenv("AI_PROVIDER", "auto")

    if ai_provider == "openai" or (ai_provider == "auto" and openai_key):
        if openai_key:
            print("✅ OpenAI API key configured")
        else:
            print("⚠️  OpenAI API key not configured")
    elif ai_provider == "gemini" or (ai_provider == "auto" and gemini_key):
        if gemini_key:
            print("✅ Gemini API key configured")
        else:
            print("⚠️  Gemini API key not configured")
    else:
        print(
            "⚠️  No AI provider API keys configured. AI functionality will be disabled."
        )
        print(
            "   To enable AI: Set OPENAI_API_KEY or GEMINI_API_KEY environment variable"
        )
        print("   Or set AI_PROVIDER=openai or AI_PROVIDER=gemini")

    # Check Python environment
    try:
        import flask

        print("✅ Flask available")
    except ImportError:
        print("❌ Flask not available. Run: pip install -r requirements.txt")
        return False

    try:
        import openai

        print("✅ OpenAI SDK available")
    except ImportError:
        print("⚠️  OpenAI SDK not available. OpenAI functionality will be disabled.")

    try:
        import google.generativeai

        print("✅ Gemini SDK available")
    except ImportError:
        print("⚠️  Gemini SDK not available. Gemini functionality will be disabled.")

    return True


def create_env_example():
    """Create example environment file."""
    env_content = """# Smart CloudOps AI - Environment Configuration
# Copy this file to .env and fill in your values

# Flask Configuration
FLASK_ENV=development
DEBUG=true
    PORT=3003

# AI Provider Configuration (Required for Phase 2.2)
AI_PROVIDER=auto  # "openai", "gemini", or "auto"

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.3

# Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-pro
GEMINI_MAX_TOKENS=500
GEMINI_TEMPERATURE=0.3

# Monitoring Configuration
PROMETHEUS_URL=http://localhost:9090
METRICS_PORT=9090

# Logging Configuration
LOG_LEVEL=INFO
LOG_DIR=logs
"""

    with open(".env.example", "w") as f:
        f.write(env_content)

    print("📄 Created .env.example file")
    print("   Copy to .env and configure your settings")


def start_application():
    """Start the Flask application."""
    print("\n🚀 Starting Smart CloudOps AI Application...")

    # Set default environment if not set
    if not os.getenv("FLASK_ENV"):
        os.environ["FLASK_ENV"] = "development"

    if not os.getenv("PORT"):
        os.environ["PORT"] = "3003"

    # Start the application
    try:
        from app.main import main

        main()
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {str(e)}")
        return False

    return True


def main():
    """Main startup function."""
    print("=" * 50)
    print("Smart CloudOps AI - Application Startup")
    print("=" * 50)

    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix issues above.")
        return 1

    print("\n✅ Environment check passed!")

    # Ask user if they want to start
    response = input("\n🚀 Start the application? (y/n): ").lower().strip()
    if response not in ["y", "yes"]:
        print("👋 Startup cancelled")
        return 0

    # Start application
    return 0 if start_application() else 1


if __name__ == "__main__":
    sys.exit(main())
