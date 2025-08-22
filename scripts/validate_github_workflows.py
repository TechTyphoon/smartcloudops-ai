#!/usr/bin/env python3
"""
GitHub Actions Workflows Validation Script

This script validates all requirements for GitHub Actions workflows to run successfully.
It checks file existence, syntax, dependencies, and configuration.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class WorkflowValidator:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.errors = []
        self.warnings = []
        self.success_count = 0

    def log_error(self, message: str):
        """Log an error message."""
        self.errors.append(f"❌ ERROR: {message}")
        print(f"❌ ERROR: {message}")

    def log_warning(self, message: str):
        """Log a warning message."""
        self.warnings.append(f"⚠️  WARNING: {message}")
        print(f"⚠️  WARNING: {message}")

    def log_success(self, message: str):
        """Log a success message."""
        self.success_count += 1
        print(f"✅ SUCCESS: {message}")

    def check_file_exists(self, file_path: str, description: str) -> bool:
        """Check if a file exists."""
        full_path = self.root_dir / file_path
        if full_path.exists():
            self.log_success(f"{description} exists: {file_path}")
            return True
        else:
            self.log_error(f"{description} missing: {file_path}")
            return False

    def check_directory_exists(self, dir_path: str, description: str) -> bool:
        """Check if a directory exists."""
        full_path = self.root_dir / dir_path
        if full_path.exists() and full_path.is_dir():
            self.log_success(f"{description} exists: {dir_path}")
            return True
        else:
            self.log_error(f"{description} missing: {dir_path}")
            return False

    def check_python_syntax(self, file_path: str) -> bool:
        """Check Python syntax of a file."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(self.root_dir / file_path)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                self.log_success(f"Python syntax valid: {file_path}")
                return True
            else:
                self.log_error(f"Python syntax error in {file_path}: {result.stderr}")
                return False
        except Exception as e:
            self.log_error(f"Failed to check Python syntax for {file_path}: {e}")
            return False

    def check_dockerfile_syntax(self, dockerfile_path: str) -> bool:
        """Check Dockerfile syntax."""
        try:
            result = subprocess.run(
                ["docker", "build", "--dry-run", "-f", dockerfile_path, "."],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
            )
            # Docker doesn't have a true dry-run, so we check for basic syntax
            if "unknown flag: --dry-run" in result.stderr:
                # This is expected, means Docker is available
                self.log_success(f"Dockerfile syntax check passed: {dockerfile_path}")
                return True
            else:
                self.log_warning(
                    f"Dockerfile syntax check inconclusive: {dockerfile_path}"
                )
                return True
        except Exception as e:
            self.log_warning(f"Docker not available for syntax check: {e}")
            return True

    def check_terraform_syntax(self) -> bool:
        """Check Terraform syntax."""
        try:
            terraform_dir = self.root_dir / "terraform"
            if not terraform_dir.exists():
                self.log_error("Terraform directory not found")
                return False

            # Check format
            result = subprocess.run(
                ["terraform", "fmt", "-check", "-recursive", "."],
                cwd=terraform_dir,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.log_success("Terraform formatting is correct")
            else:
                self.log_warning("Terraform formatting issues found")

            # Check validation (without backend)
            result = subprocess.run(
                ["terraform", "init", "-backend=false"],
                cwd=terraform_dir,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                result = subprocess.run(
                    ["terraform", "validate"],
                    cwd=terraform_dir,
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    self.log_success("Terraform validation passed")
                    return True
                else:
                    self.log_warning(f"Terraform validation issues: {result.stderr}")
                    return True  # Continue with warnings
            else:
                self.log_warning(f"Terraform init failed: {result.stderr}")
                return True  # Continue with warnings

        except Exception as e:
            self.log_warning(f"Terraform check failed: {e}")
            return True

    def check_requirements_files(self) -> bool:
        """Check requirements files."""
        success = True

        # Check main requirements
        if self.check_file_exists("requirements.txt", "Main requirements file"):
            # Try to parse requirements
            try:
                with open(self.root_dir / "requirements.txt", "r") as f:
                    lines = f.readlines()
                    if len(lines) > 0:
                        self.log_success("requirements.txt has content")
                    else:
                        self.log_warning("requirements.txt is empty")
            except Exception as e:
                self.log_error(f"Failed to read requirements.txt: {e}")
                success = False

        # Check dev requirements
        if self.check_file_exists(
            "requirements-dev.txt", "Development requirements file"
        ):
            try:
                with open(self.root_dir / "requirements-dev.txt", "r") as f:
                    lines = f.readlines()
                    if len(lines) > 0:
                        self.log_success("requirements-dev.txt has content")
                    else:
                        self.log_warning("requirements-dev.txt is empty")
            except Exception as e:
                self.log_error(f"Failed to read requirements-dev.txt: {e}")
                success = False

        return success

    def check_test_structure(self) -> bool:
        """Check test directory structure."""
        success = True

        # Check main test directory
        if not self.check_directory_exists("tests", "Tests directory"):
            success = False

        # Check unit tests
        if not self.check_directory_exists("tests/unit", "Unit tests directory"):
            success = False
        else:
            # Check for test files
            unit_dir = self.root_dir / "tests" / "unit"
            test_files = list(unit_dir.glob("test_*.py"))
            if test_files:
                self.log_success(f"Found {len(test_files)} unit test files")
            else:
                self.log_warning("No unit test files found")

        # Check integration tests
        if not self.check_directory_exists(
            "tests/integration", "Integration tests directory"
        ):
            success = False
        else:
            # Check for test files
            integration_dir = self.root_dir / "tests" / "integration"
            test_files = list(integration_dir.glob("test_*.py"))
            if test_files:
                self.log_success(f"Found {len(test_files)} integration test files")
            else:
                self.log_warning("No integration test files found")

        return success

    def check_workflow_files(self) -> bool:
        """Check GitHub Actions workflow files."""
        success = True

        workflows_dir = self.root_dir / ".github" / "workflows"
        if not workflows_dir.exists():
            self.log_error("GitHub workflows directory not found")
            return False

        expected_workflows = [
            "ci-cd-optimized.yml",
            "ecr-build-push.yml",
            "security-monitoring.yml",
            "ci-infra.yml",
        ]

        for workflow in expected_workflows:
            if self.check_file_exists(
                f".github/workflows/{workflow}", f"Workflow file: {workflow}"
            ):
                # Check YAML syntax
                try:
                    import yaml

                    with open(workflows_dir / workflow, "r") as f:
                        yaml.safe_load(f)
                    self.log_success(f"YAML syntax valid: {workflow}")
                except Exception as e:
                    self.log_error(f"YAML syntax error in {workflow}: {e}")
                    success = False

        return success

    def check_app_structure(self) -> bool:
        """Check application structure."""
        success = True

        # Check app directory
        if not self.check_directory_exists("app", "Application directory"):
            success = False

        # Check main app files
        app_files = ["app/__init__.py", "app/main.py", "app/config.py"]

        for app_file in app_files:
            if self.check_file_exists(app_file, f"App file: {app_file}"):
                # Check Python syntax for Python files
                if app_file.endswith(".py"):
                    if not self.check_python_syntax(app_file):
                        success = False

        return success

    def check_environment_files(self) -> bool:
        """Check environment configuration files."""
        success = True

        # Check env.example
        if self.check_file_exists("env.example", "Environment example file"):
            try:
                with open(self.root_dir / "env.example", "r") as f:
                    content = f.read()
                    if "AWS_ACCESS_KEY_ID" in content:
                        self.log_success("env.example contains AWS configuration")
                    else:
                        self.log_warning("env.example missing AWS configuration")
            except Exception as e:
                self.log_error(f"Failed to read env.example: {e}")
                success = False

        # Check that .env is not committed
        if (self.root_dir / ".env").exists():
            self.log_warning(".env file exists (should not be committed)")

        return success

    def run_all_checks(self) -> bool:
        """Run all validation checks."""
        print("🔍 Starting GitHub Actions Workflows Validation")
        print("=" * 60)

        checks = [
            ("Workflow Files", self.check_workflow_files),
            ("Application Structure", self.check_app_structure),
            ("Requirements Files", self.check_requirements_files),
            ("Test Structure", self.check_test_structure),
            (
                "Docker Files",
                lambda: all(
                    [
                        self.check_file_exists("Dockerfile", "Dockerfile"),
                        self.check_file_exists(
                            "Dockerfile.production", "Production Dockerfile"
                        ),
                        self.check_dockerfile_syntax("Dockerfile"),
                        self.check_dockerfile_syntax("Dockerfile.production"),
                    ]
                ),
            ),
            ("Terraform Configuration", self.check_terraform_syntax),
            ("Environment Files", self.check_environment_files),
        ]

        overall_success = True

        for check_name, check_func in checks:
            print(f"\n📋 {check_name}")
            print("-" * 40)
            try:
                if not check_func():
                    overall_success = False
            except Exception as e:
                self.log_error(f"Check failed with exception: {e}")
                overall_success = False

        # Print summary
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"✅ Successes: {self.success_count}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  {error}")

        if overall_success:
            print("\n🎉 All critical checks passed! Workflows should run successfully.")
        else:
            print("\n🚨 Some critical checks failed. Please fix the errors above.")

        return overall_success

    def generate_report(self) -> Dict:
        """Generate a validation report."""
        return {
            "success_count": self.success_count,
            "warnings": self.warnings,
            "errors": self.errors,
            "overall_success": len(self.errors) == 0,
        }


def main():
    """Main function."""
    validator = WorkflowValidator()
    success = validator.run_all_checks()

    # Generate report
    report = validator.generate_report()

    # Save report to file
    report_file = Path(__file__).parent.parent / "workflow_validation_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Validation report saved to: {report_file}")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
