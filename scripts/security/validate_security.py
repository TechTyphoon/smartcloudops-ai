#!/usr/bin/env python3
"""
Security Validation Script for SmartCloudOps AI
Comprehensive security checks and validation
"""

import json
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app"))

from security.config import validate_environment_security

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SecurityValidator:
    """Comprehensive security validation for SmartCloudOps AI."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.results = {
            "overall_status": "PASS",
            "checks": {},
            "recommendations": [],
            "critical_issues": [],
            "warnings": [],
        }

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all security validation checks."""
        logger.info("🔒 Starting comprehensive security validation...")

        checks = [
            ("environment_security", self.check_environment_security),
            ("file_permissions", self.check_file_permissions),
            ("secrets_management", self.check_secrets_management),
            ("dependencies_security", self.check_dependencies_security),
            ("code_security", self.check_code_security),
            ("docker_security", self.check_docker_security),
            ("terraform_security", self.check_terraform_security),
            ("ci_cd_security", self.check_ci_cd_security),
        ]

        for check_name, check_func in checks:
            try:
                logger.info(f"Running {check_name} check...")
                self.results["checks"][check_name] = check_func()
            except Exception as e:
                logger.error(f"Error in {check_name} check: {e}")
                self.results["checks"][check_name] = {
                    "status": "ERROR",
                    "error": str(e),
                }

        self._evaluate_overall_status()
        return self.results

    def check_environment_security(self) -> Dict[str, Any]:
        """Check environment security configuration."""
        result = {"status": "PASS", "issues": [], "warnings": []}

        # Validate environment variables
        env_validation = validate_environment_security()

        if not env_validation["secure"]:
            result["status"] = "FAIL"
            result["issues"].extend(env_validation["missing_variables"])
            result["warnings"].extend(env_validation["weak_variables"])

        # Check for hardcoded secrets in files
        secret_files = self._find_hardcoded_secrets()
        if secret_files:
            result["status"] = "FAIL"
            result["issues"].extend(secret_files)

        return result

    def check_file_permissions(self) -> Dict[str, Any]:
        """Check file permissions for security."""
        result = {"status": "PASS", "issues": [], "warnings": []}

        sensitive_files = [
            ".env*",
            "*.key",
            "*.pem",
            "*.crt",
            "secrets*",
            "terraform.tfvars*",
        ]

        for pattern in sensitive_files:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file():
                    stat = file_path.stat()
                    mode = oct(stat.st_mode)[-3:]

                    # Check if file is world-readable
                    if int(mode[-1]) >= 4:
                        result["warnings"].append(
                            f"File {file_path.relative_to(self.project_root)} "
                            f"is world-readable (mode: {mode})"
                        )

                    # Check if file is world-writable
                    if int(mode[-1]) >= 2:
                        result["status"] = "FAIL"
                        result["issues"].append(
                            f"File {file_path.relative_to(self.project_root)} "
                            f"is world-writable (mode: {mode})"
                        )

        return result

    def check_secrets_management(self) -> Dict[str, Any]:
        """Check secrets management practices."""
        result = {"status": "PASS", "issues": [], "warnings": []}

        # Check for hardcoded secrets in code
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
        ]

        code_files = (
            list(self.project_root.rglob("*.py"))
            + list(self.project_root.rglob("*.yml"))
            + list(self.project_root.rglob("*.yaml"))
        )

        for file_path in code_files:
            if file_path.name in [".gitignore", "requirements.txt"]:
                continue

            try:
                content = file_path.read_text()
                for pattern in secret_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1
                        result["warnings"].append(
                            f"Potential hardcoded secret in {file_path.relative_to(self.project_root)}:"
                            f"{line_num}: {match.group()[:50]}..."
                        )
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")

        return result

    def check_dependencies_security(self) -> Dict[str, Any]:
        """Check dependencies for security vulnerabilities."""
        result = {"status": "PASS", "issues": [], "warnings": []}

        try:
            # Check if safety is available
            subprocess.run(["safety", "--version"], capture_output=True, check=True)

            # Run safety check
            safety_result = subprocess.run(
                ["safety", "check", "--json"], capture_output=True, text=True
            )

            if safety_result.returncode != 0:
                try:
                    vulnerabilities = json.loads(safety_result.stdout)
                    if vulnerabilities:
                        result["status"] = "FAIL"
                        for vuln in vulnerabilities:
                            result["issues"].append(
                                f"Vulnerability in {vuln.get('package', 'unknown')}: "
                                f"{vuln.get('description', 'No description')}"
                            )
                except json.JSONDecodeError:
                    result["warnings"].append("Could not parse safety output")

        except (subprocess.CalledProcessError, FileNotFoundError):
            result["warnings"].append(
                "Safety not available - install with: pip install safety"
            )

        return result

    def check_code_security(self) -> Dict[str, Any]:
        """Check code for security issues."""
        result = {"status": "PASS", "issues": [], "warnings": []}

        try:
            # Check if bandit is available
            subprocess.run(["bandit", "--version"], capture_output=True, check=True)

            # Run bandit check
            bandit_result = subprocess.run(
                ["bandit", "-r", "app/", "-f", "json"], capture_output=True, text=True
            )

            if bandit_result.returncode != 0:
                try:
                    issues = json.loads(bandit_result.stdout)
                    if issues.get("results"):
                        for issue in issues["results"]:
                            severity = issue.get("issue_severity", "LOW")
                            if severity in ["HIGH", "MEDIUM"]:
                                result["status"] = "FAIL"
                                result["issues"].append(
                                    f"{severity} issue in {issue.get('filename', 'unknown')}:"
                                    f"{issue.get('line_number', 'unknown')}: "
                                    f"{issue.get('issue_text', 'No description')}"
                                )
                            else:
                                result["warnings"].append(
                                    f"LOW issue in {issue.get('filename', 'unknown')}:"
                                    f"{issue.get('line_number', 'unknown')}: "
                                    f"{issue.get('issue_text', 'No description')}"
                                )
                except json.JSONDecodeError:
                    result["warnings"].append("Could not parse bandit output")

        except (subprocess.CalledProcessError, FileNotFoundError):
            result["warnings"].append(
                "Bandit not available - install with: pip install bandit"
            )

        return result

    def check_docker_security(self) -> Dict[str, Any]:
        """Check Docker security configuration."""
        result = {"status": "PASS", "issues": [], "warnings": []}

        dockerfile_path = self.project_root / "Dockerfile.production"

        if dockerfile_path.exists():
            content = dockerfile_path.read_text()

            # Check for security best practices
            checks = [
                (r"USER\s+root", "Container runs as root user"),
                (r"apt-get\s+upgrade", "apt-get upgrade should be avoided"),
                (r"COPY\s+.*\s+/\s*$", "Copying to root directory"),
                (r"RUN\s+chmod\s+777", "Overly permissive file permissions"),
            ]

            for pattern, issue in checks:
                if re.search(pattern, content, re.IGNORECASE):
                    result["warnings"].append(f"Docker security: {issue}")

        return result

    def check_terraform_security(self) -> Dict[str, Any]:
        """Check Terraform security configuration."""
        result = {"status": "PASS", "issues": [], "warnings": []}

        terraform_dir = self.project_root / "terraform"

        if terraform_dir.exists():
            # Check for hardcoded secrets in Terraform files
            tf_files = list(terraform_dir.rglob("*.tf")) + list(
                terraform_dir.rglob("*.tfvars")
            )

            for file_path in tf_files:
                try:
                    content = file_path.read_text()

                    # Check for hardcoded passwords
                    password_patterns = [
                        r'password\s*=\s*["\'][^"\']+["\']',
                        r'secret\s*=\s*["\'][^"\']+["\']',
                        r'key\s*=\s*["\'][^"\']+["\']',
                    ]

                    for pattern in password_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            result["warnings"].append(
                                f"Potential hardcoded secret in {file_path.relative_to(self.project_root)}"
                            )

                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")

        return result

    def check_ci_cd_security(self) -> Dict[str, Any]:
        """Check CI/CD security configuration."""
        result = {"status": "PASS", "issues": [], "warnings": []}

        workflows_dir = self.project_root / ".github" / "workflows"

        if workflows_dir.exists():
            workflow_files = list(workflows_dir.rglob("*.yml")) + list(
                workflows_dir.rglob("*.yaml")
            )

            for file_path in workflow_files:
                try:
                    content = file_path.read_text()

                    # Check for overly permissive permissions
                    if "permissions:" in content:
                        if "contents: write" in content:
                            result["warnings"].append(
                                f"Overly permissive permissions in {file_path.relative_to(self.project_root)}"
                            )

                    # Check for plaintext secrets
                    secret_patterns = [
                        r'password:\s*["\'][^"\']+["\']',
                        r'secret:\s*["\'][^"\']+["\']',
                        r'token:\s*["\'][^"\']+["\']',
                    ]

                    for pattern in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            result["issues"].append(
                                f"Plaintext secret in {file_path.relative_to(self.project_root)}"
                            )

                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")

        return result

    def _find_hardcoded_secrets(self) -> List[str]:
        """Find files with potential hardcoded secrets."""
        issues = []

        # Check for files that might contain secrets
        secret_indicators = [
            "password",
            "secret",
            "key",
            "token",
            "credential",
        ]

        for indicator in secret_indicators:
            for file_path in self.project_root.rglob(f"*{indicator}*"):
                if file_path.is_file() and not self._is_ignored_file(file_path):
                    try:
                        content = file_path.read_text()
                        if re.search(
                            rf'{indicator}\s*[=:]\s*["\'][^"\']+["\']',
                            content,
                            re.IGNORECASE,
                        ):
                            issues.append(
                                f"Potential hardcoded {indicator} in {file_path.relative_to(self.project_root)}"
                            )
                    except Exception:
                        pass

        return issues

    def _is_ignored_file(self, file_path: Path) -> bool:
        """Check if file should be ignored in security checks."""
        ignored_patterns = [
            ".git/",
            "__pycache__/",
            ".venv/",
            "venv/",
            "node_modules/",
            ".pytest_cache/",
            "*.pyc",
            "*.log",
        ]

        file_str = str(file_path)
        return any(pattern in file_str for pattern in ignored_patterns)

    def _evaluate_overall_status(self):
        """Evaluate overall security status."""
        critical_issues = []
        warnings = []

        for check_name, check_result in self.results["checks"].items():
            if check_result.get("status") == "FAIL":
                critical_issues.extend(check_result.get("issues", []))
                self.results["overall_status"] = "FAIL"

            warnings.extend(check_result.get("warnings", []))

        self.results["critical_issues"] = critical_issues
        self.results["warnings"] = warnings

        # Generate recommendations
        if critical_issues:
            self.results["recommendations"].append(
                "Fix all critical security issues before deployment"
            )

        if warnings:
            self.results["recommendations"].append(
                "Address security warnings to improve overall security posture"
            )

        if not critical_issues and not warnings:
            self.results["recommendations"].append(
                "Security validation passed! Continue with deployment."
            )


def main():
    """Main function to run security validation."""
    validator = SecurityValidator()
    results = validator.run_all_checks()

    # Print results
    print("\n" + "=" * 60)
    print("🔒 SECURITY VALIDATION RESULTS")
    print("=" * 60)

    print(f"\nOverall Status: {results['overall_status']}")

    if results["critical_issues"]:
        print(f"\n❌ Critical Issues ({len(results['critical_issues'])}):")
        for issue in results["critical_issues"]:
            print(f"  • {issue}")

    if results["warnings"]:
        print(f"\n⚠️  Warnings ({len(results['warnings'])}):")
        for warning in results["warnings"][:10]:  # Limit to first 10 warnings
            print(f"  • {warning}")
        if len(results["warnings"]) > 10:
            print(f"  ... and {len(results['warnings']) - 10} more warnings")

    if results["recommendations"]:
        print(f"\n💡 Recommendations:")
        for rec in results["recommendations"]:
            print(f"  • {rec}")

    # Save detailed results to file
    output_file = Path(__file__).parent / "security_validation_report.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Detailed report saved to: {output_file}")

    # Exit with appropriate code
    if results["overall_status"] == "FAIL":
        print("\n❌ Security validation FAILED. Fix issues before deployment.")
        sys.exit(1)
    else:
        print("\n✅ Security validation PASSED.")
        sys.exit(0)


if __name__ == "__main__":
    main()
