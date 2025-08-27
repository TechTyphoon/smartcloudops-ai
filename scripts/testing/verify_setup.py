#!/usr/bin/env python3
"""
Smart CloudOps AI - Setup Verification Script
This script verifies that Phase 0 setup is complete and working correctly.
"""

import os
import subprocess


def check_file_exists(file_path, description):
    """Check if a file exists."""""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - Missing")
        return False


def check_directory_exists(dir_path, description):
    """Check if a directory exists."""""
    if Path(dir_path).is_dir():
        print(f"✅ {description}: {dir_path}/")
        return True
    else:
        print(f"❌ {description}: {dir_path}/ - Missing")
        return False


def run_command_check(command, description):
    """Run a command and check if it succeeds."""""
    import shlex

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
            timeout=30,  # Add timeout for security
        )
        if result.returncode == 0:
            print(f"✅ {description}: Available")
            return True
        else:
            print(f"❌ {description}: Not available or not working")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {description}: Command timed out")
        return False
    except Exception as e:
        print(f"❌ {description}: Error - {str(e)}")
        return False


def verify_phase_0():
    """Verify Phase 0 completion."""""
    print("🔍 Smart CloudOps AI - Phase 0 Verification")
    print("=" * 50)

    passed_checks = 0
    total_checks = 0

    # Check required files
    print("\n📁 Checking Project Files:")
    files_to_check = [
        ("README.md", "Main documentation"),
        (".gitignore", "Git ignore file"),
        ("LICENSE", "License file"),
        ("requirements.txt", "Python dependencies"),
        ("Dockerfile", "Container configuration"),
        ("docker-compose.yml", "Development stack"),
        ("setup.py", "Setup script"),
        ("SMART_CLOUDOPS_AI_PROJECT_PLAN.md", "Project plan"),
    ]

    for file_path, description in files_to_check:
        total_checks += 1
        if check_file_exists(file_path, description):
            passed_checks += 1

    # Check required directories
    print("\n📂 Checking Project Directories:")
    directories_to_check = [
        ("terraform", "Infrastructure code"),
        ("app", "Flask application"),
        ("scripts", "Automation scripts"),
        ("ml_models", "ML models"),
        (".github/workflows", "CI/CD pipelines"),
        ("docs", "Documentation"),
    ]

    for dir_path, description in directories_to_check:
        total_checks += 1
        if check_directory_exists(dir_path, description):
            passed_checks += 1

    # Check CI/CD workflows
    print("\n🔄 Checking CI/CD Workflows:")
    workflow_files = [
        (".github/workflows/ci-infra.yml", "Infrastructure pipeline"),
        (".github/workflows/ci-app.yml", "Application pipeline"),
    ]

    for file_path, description in workflow_files:
        total_checks += 1
        if check_file_exists(file_path, description):
            passed_checks += 1

    # Check if tools are available (optional checks)
    print("\n🛠️ Checking Available Tools (Optional):")
    tools_to_check = [
        ("python3 --version", "Python 3"),
        ("docker --version", "Docker"),
        ("terraform --version", "Terraform"),
        ("git --version", "Git"),
    ]

    optional_passed = 0
    for command, description in tools_to_check:
        if run_command_check(command, description):
            optional_passed += 1

    # Check file permissions
    print("\n🔐 Checking File Permissions:")
    total_checks += 1
    if os.access("setup.py", os.X_OK):
        print("✅ setup.py is executable")
        passed_checks += 1
    else:
        print("❌ setup.py is not executable")

    # Summary
    print("\n" + "=" * 50)
    print("📊 Verification Summary:")
    print(f"Required checks passed: {passed_checks}/{total_checks}")
    print(f"Optional tools available: {optional_passed}/{len(tools_to_check)}")

    if passed_checks == total_checks:
        print("🎉 Phase 0 setup is COMPLETE! ✅")
        print("\n📋 Ready for Phase 1:")
        print("- Infrastructure Provisioning + Monitoring")
        print("- Run: python3 setup.py (to set up development environment)")
        print("- Run: docker-compose up -d (to start local development stack)")
        return True
    else:
        print("❌ Phase 0 setup is INCOMPLETE!")
        print(f"Missing {total_checks - passed_checks} required components.")
        print("Please review the missing items above.")
        return False


def main():
    """Main verification function."""""
    success = verify_phase_0()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
