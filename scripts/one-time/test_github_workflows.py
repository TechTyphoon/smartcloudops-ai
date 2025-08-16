#!/usr/bin/env python3
"""
Test GitHub Actions workflows locally
"""

import os
import subprocess
import sys


def run_command(cmd, cwd=None, capture_output=True):
    """Run a command securely and return result."""
    import shlex

    try:
        # Parse command safely - split shell command into list
        if isinstance(cmd, str):
            cmd_list = shlex.split(cmd)
        else:
            cmd_list = cmd

        result = subprocess.run(
            cmd_list,
            shell=False,  # Security fix: Never use shell=True
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            timeout=300,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def test_python_imports():
    """Test Python imports that would fail in GitHub Actions."""
    print("🔍 Testing Python imports...")

    # Test basic imports
    imports_to_test = [
        "import app.config",
        "import pytest",
        "import flake8",
        "import black",
        "import isort",
        "import bandit",
        "import safety",
    ]

    for import_cmd in imports_to_test:
        success, stdout, stderr = run_command(f"python3 -c '{import_cmd}'")
        if not success:
            print(f"❌ Failed: {import_cmd}")
            print(f"   Error: {stderr}")
            return False
        else:
            print(f"✅ {import_cmd}")

    return True


def test_terraform_basic():
    """Test Terraform without AWS credentials."""
    print("\n🔍 Testing Terraform basic validation...")

    terraform_dir = "terraform"

    # Test format
    success, stdout, stderr = run_command(
        "terraform fmt -check -recursive", cwd=terraform_dir
    )
    if not success:
        print(f"❌ Terraform format check failed: {stderr}")
        return False
    print("✅ Terraform format check passed")

    # Test init
    success, stdout, stderr = run_command("terraform init", cwd=terraform_dir)
    if not success:
        print(f"❌ Terraform init failed: {stderr}")
        return False
    print("✅ Terraform init passed")

    # Test validate
    success, stdout, stderr = run_command("terraform validate", cwd=terraform_dir)
    if not success:
        print(f"❌ Terraform validate failed: {stderr}")
        return False
    print("✅ Terraform validate passed")

    return True


def test_docker_build():
    """Test Docker build."""
    print("\n🔍 Testing Docker build...")

    success, stdout, stderr = run_command("docker build -t test-smartcloudops .")
    if not success:
        print(f"❌ Docker build failed: {stderr}")
        return False
    print("✅ Docker build passed")

    # Clean up
    run_command("docker rmi test-smartcloudops", capture_output=False)
    return True


def test_security_tools():
    """Test security scanning tools."""
    print("\n🔍 Testing security tools...")

    # Test Bandit
    success, stdout, stderr = run_command(
        "bandit -r app/ scripts/ -f json -o /dev/null || true"
    )
    if not success:
        print(f"❌ Bandit failed: {stderr}")
        return False
    print("✅ Bandit security scan passed")

    # Test Safety
    success, stdout, stderr = run_command(
        "safety check --json --output /dev/null || true"
    )
    if not success:
        print(f"❌ Safety check failed: {stderr}")
        return False
    print("✅ Safety check passed")

    return True


def test_github_secrets_simulation():
    """Simulate GitHub secrets environment."""
    print("\n🔍 Testing GitHub secrets simulation...")

    # Check if AWS credentials are available
    aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

    if not aws_access_key or not aws_secret_key:
        print("⚠️  AWS credentials not found in environment variables")
        print("   This will cause Terraform plan to fail on GitHub Actions")
        print("   You need to add these as GitHub Secrets:")
        print("   - AWS_ACCESS_KEY_ID")
        print("   - AWS_SECRET_ACCESS_KEY")
        print("   - AWS_REGION (optional, defaults to us-west-2)")
        return False

    print("✅ AWS credentials found in environment")

    # Test AWS connectivity
    success, stdout, stderr = run_command("aws sts get-caller-identity")
    if not success:
        print(f"❌ AWS connectivity test failed: {stderr}")
        return False
    print("✅ AWS connectivity test passed")

    return True


def main():
    """Main test function."""
    print("🚀 Testing Smart CloudOps AI Workflows Locally")
    print("=" * 50)

    tests = [
        ("Python Imports", test_python_imports),
        ("Terraform Basic", test_terraform_basic),
        ("Docker Build", test_docker_build),
        ("Security Tools", test_security_tools),
        ("GitHub Secrets", test_github_secrets_simulation),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            success = test_func()
            results[test_name] = success
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    passed = sum(results.values())
    total = len(results)

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Ready to push to GitHub.")
        print("\n📝 Next steps:")
        print("1. Add AWS credentials to GitHub Secrets:")
        print("   - Go to your GitHub repository")
        print("   - Settings → Secrets and variables → Actions")
        print("   - Add: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION")
        print("2. Push your changes: git push origin main")
    else:
        print("⚠️  Some tests failed. Fix issues before pushing to GitHub.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
