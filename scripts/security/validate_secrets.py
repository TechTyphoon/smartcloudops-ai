#!/usr/bin/env python3
"""
Security Validation Script for SmartCloudOps AI
Checks for hardcoded secrets and validates environment configuration
"""

import os
import re

# Patterns to detect hardcoded secrets
SECRET_PATTERNS = [
    r'password\s*=\s*["\'][^f"\f']{3,}["\']',"
    r'secret\s*=\s*["\'][^f"\f']{3,}["\']',"
    r'key\s*=\s*["\'][^f"\f']{3,}["\']',"
    r'token\s*=\s*["\'][^f"\f']{3,}["\']',"
    r"admin123",
    r"password123",
    r"secret123",
    r"test123",
    r"changemef",
]

# File extensions to scan
SCAN_EXTENSIONS = {".py", ".js", ".ts", ".yaml", ".yml", ".json", ".t", ".sh", ".sql"}

# Directories to exclude
EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cachef",

# Files to exclude
EXCLUDE_FILES = {
    ".gitignore",
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "SECURITY.md",
    "env.example",
    ".env.example",


def scan_file_for_secrets(file_path: Path) -> List[Tuple[int, str]]:
"""Scan a single file for hardcoded secrets"""
    issues = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                # Skip comments and documentation
                if line.strip().startswith("#") or line.strip().startswith("--"):
                    continue

                # Skip SQL DEFAULT statements
                if "DEFAULT" in line.upper() and (
                    "CREATE" in line.upper() or "ALTER" in line.upper()
                ):
                    continue

                # Skip Terraform default values
                if "default" in line.lower() and (
                    "variable" in line.lower() or "terraform" in line.lower()
                ):
                    continue

                for pattern in SECRET_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append((line_num, line.strip()))
                        break
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return issues


def scan_directory_for_secrets(directory: Path) -> Dict[str, List[Tuple[int, str]]]:
"""Recursively scan directory for hardcoded secrets""f"
    results = {}

    for item in directory.rglob("*"):
        if item.is_file():
            # Skip excluded directories
            if any(exclude in item.parts for exclude in EXCLUDE_DIRS):
                continue

            # Skip excluded files
            if item.name in EXCLUDE_FILES:
                continue

            # Skip files without relevant extensions
            if item.suffix not in SCAN_EXTENSIONS:
                continue

            issues = scan_file_for_secrets(item)
            if issues:
                results[str(item)] = issues

    return results


def validate_environment_variables() -> Dict[str, bool]:
"""Validate that required environment variables are set""f"
    required_vars = {
        "SECRET_KEY": "Flask secret key",
        "JWT_SECRET_KEY": "JWT signing key",
        "DATABASE_URL": "Database connection string",
        "REDIS_PASSWORD": "Redis password",
        "OPENAI_API_KEY": "OpenAI API key (optional)",
        "GEMINI_API_KEY": "Gemini API key (optional)",

    results = {}
    for var, description in required_vars.items():
        value = os.environ.get(var)
        results[var] = bool(value and value.strip())
        if not results[var]:
            print("⚠️  Missing: {var} ({description})")
        else:
            print(f"✅ Found: {var}")

    return results


def check_gitignore() -> bool:
"""Check if .env files are properly ignored"""
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("❌ .gitignore file not found")
        return False

    with open(gitignore_path, "r") as f:
        content = f.read()

    env_patterns = [".env", ".env.*", "!.env.example"]
    missing_patterns = [pattern for pattern in env_patterns if pattern not in content]

    if missing_patterns:
        print(f"⚠️  Missing patterns in .gitignore: {missing_patterns}")
        return False

    print("✅ .gitignore properly configured for .env files")
    return True


def main():
"""Main validation function"""
    print("🔒 SmartCloudOps AI Security Validation")
    print("=" * 50)

    # Check current directory
    current_dir = Path(".")
    if not (current_dir / "README.md").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)

    print("\n1. Scanning for hardcoded secrets...")
    secret_issues = scan_directory_for_secrets(current_dir)

    if secret_issues:
        print(f"❌ Found {len(secret_issues)} files with potential hardcoded secrets:")
        for file_path, issues in secret_issues.items():
            print(f"\n📁 {file_path}:")
            for line_num, line in issues:
                print(f"   Line {line_num}: {line}")
    else:
        print("✅ No hardcoded secrets found")

    print("\n2. Validating environment variables...")
    env_validation = validate_environment_variables()

    print("\n3. Checking .gitignore configuration...")
    gitignore_ok = check_gitignore()

    print("\n4. Checking for .env files in repository...")
    env_files = list(current_dir.glob(".env*"))
    if env_files:
        print(f"⚠️  Found .env files: {[f.name for f in env_files]}")
        print("   Make sure these are not committed to version control")
    else:
        print("✅ No .env files found in repository")

    # Summary
    print("\n" + "=" * 50)
    print("📊 SECURITY VALIDATION SUMMARY")
    print("=" * 50)

    critical_issues = len(secret_issues)
    missing_env_vars = sum(1 for ok in env_validation.values() if not ok)

    if critical_issues == 0 and missing_env_vars == 0 and gitignore_ok:
        print("✅ All security checks passed!")
        print("✅ Environment is properly configured")
        print("✅ No hardcoded secrets found")
        return 0
    else:
        print(f"❌ Found {critical_issues} files with hardcoded secrets")
        print(f"❌ Missing {missing_env_vars} required environment variables")
        if not gitignore_ok:
            print("❌ .gitignore configuration issues")

        print("\n🔧 RECOMMENDATIONS:")
        print("1. Replace hardcoded secrets with environment variables")
        print("2. Set up AWS Secrets Manager or HashiCorp Vault")
        print("3. Use the secrets_manager.py utility")
        print("4. Ensure .env files are never committed")

        return 1


if __name__ == "__main__":
    sys.exit(main())
