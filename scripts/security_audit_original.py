#!/usr/bin/env python3
"""
Comprehensive Security Audit Script for Smart CloudOps AI
Phase 6.1: Security Audit & Vulnerability Assessment
"""

import hashlib
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SecurityAuditor:
    """Comprehensive security audit for Smart CloudOps AI project."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.audit_results = {
            "timestamp": "",
            "overall_score": 0,
            "critical_issues": [],
            "high_issues": [],
            "medium_issues": [],
            "low_issues": [],
            "info_issues": [],
            "recommendations": [],
            "dependency_scan": {},
            "code_scan": {},
            "config_scan": {},
            "infrastructure_scan": {},
        }

    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run the complete security audit."""
        logger.info("🚀 Starting Comprehensive Security Audit for Smart CloudOps AI")

        # Update timestamp
        from datetime import datetime

        self.audit_results["timestamp"] = datetime.now().isoformat()

        # Run all audit phases
        self._audit_dependencies()
        self._audit_code_security()
        self._audit_configuration_security()
        self._audit_infrastructure_security()
        self._audit_file_permissions()
        self._audit_secrets_exposure()
        self._calculate_security_score()
        self._generate_recommendations()

        return self.audit_results

    def _audit_dependencies(self):
        """Audit Python dependencies for known vulnerabilities."""
        logger.info("📦 Auditing Python dependencies...")

        try:
            # Check if bandit is available
            result = subprocess.run(
                ["bandit", "--version"], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                # Run bandit security scan
                bandit_result = subprocess.run(
                    ["bandit", "-r", str(self.project_root), "-f", "json"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if bandit_result.returncode == 0:
                    try:
                        bandit_data = json.loads(bandit_result.stdout)
                        self.audit_results["code_scan"]["bandit"] = bandit_data

                        # Categorize issues by severity
                        for issue in bandit_data.get("results", []):
                            severity = issue.get("issue_severity", "LOW").upper()
                            if severity == "HIGH":
                                self.audit_results["high_issues"].append(
                                    {
                                        "tool": "bandit",
                                        "file": issue.get("filename", "unknown"),
                                        "line": issue.get("line_number", 0),
                                        "issue": issue.get(
                                            "issue_text", "Unknown issue"
                                        ),
                                        "description": issue.get("more_info", ""),
                                    }
                                )
                            elif severity == "MEDIUM":
                                self.audit_results["medium_issues"].append(
                                    {
                                        "tool": "bandit",
                                        "file": issue.get("filename", "unknown"),
                                        "line": issue.get("line_number", 0),
                                        "issue": issue.get(
                                            "issue_text", "Unknown issue"
                                        ),
                                        "description": issue.get("more_info", ""),
                                    }
                                )
                            else:
                                self.audit_results["low_issues"].append(
                                    {
                                        "tool": "bandit",
                                        "file": issue.get("filename", "unknown"),
                                        "line": issue.get("line_number", 0),
                                        "issue": issue.get(
                                            "issue_text", "Unknown issue"
                                        ),
                                        "description": issue.get("more_info", ""),
                                    }
                                )
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse bandit output")
                else:
                    logger.warning("Bandit scan failed")
            else:
                logger.warning("Bandit not available, skipping code security scan")

        except Exception as e:
            logger.error(f"Error running bandit: {e}")

        # Check for known vulnerable packages
        self._check_vulnerable_packages()

    def _check_vulnerable_packages(self):
        """Check for known vulnerable packages in requirements."""
        logger.info("🔍 Checking for vulnerable packages...")

        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            with open(requirements_file, "r") as f:
                requirements = f.read()

            # Known vulnerable packages (example list - should be updated regularly)
            vulnerable_packages = {
                "django": "<2.2.0",
                "flask": "<2.0.0",
                "requests": "<2.25.0",
                "urllib3": "<1.26.0",
            }

            for package, min_version in vulnerable_packages.items():
                if package in requirements.lower():
                    # Check if version is specified and compare
                    version_match = re.search(
                        rf"{package}[<>=!]+([\d.]+)", requirements, re.IGNORECASE
                    )
                    if version_match:
                        version = version_match.group(1)
                        # Simple version comparison (could be enhanced)
                        if version < min_version:
                            self.audit_results["high_issues"].append(
                                {
                                    "tool": "manual",
                                    "file": "requirements.txt",
                                    "issue": f"Vulnerable package version: {package} {version}",
                                    "description": f"Minimum safe version: {min_version}",
                                }
                            )

    def _audit_code_security(self):
        """Audit code for security best practices."""
        logger.info("🔒 Auditing code security practices...")

        security_patterns = {
            "hardcoded_secrets": [
                r"password\s*=\s*['\"][^'\"]+['\"]",
                r"secret\s*=\s*['\"][^'\"]+['\"]",
                r"api_key\s*=\s*['\"][^'\"]+['\"]",
                r"token\s*=\s*['\"][^'\"]+['\"]",
            ],
            "sql_injection": [
                r"execute\s*\(\s*[^)]*\+",
                r"cursor\.execute\s*\(\s*[^)]*\+",
            ],
            "command_injection": [
                r"os\.system\s*\(",
                r"subprocess\.run\s*\(\s*[^)]*\+",
                r"eval\s*\(",
                r"exec\s*\(",
            ],
        }

        python_files = list(self.project_root.rglob("*.py"))
        for pattern_name, patterns in security_patterns.items():
            for pattern in patterns:
                for py_file in python_files:
                    try:
                        with open(py_file, "r", encoding="utf-8") as f:
                            content = f.read()

                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[: match.start()].count("\n") + 1
                            self.audit_results["medium_issues"].append(
                                {
                                    "tool": "manual",
                                    "file": str(py_file.relative_to(self.project_root)),
                                    "line": line_num,
                                    "issue": f"Potential {pattern_name}",
                                    "description": f"Pattern matched: {match.group()}",
                                }
                            )
                    except Exception as e:
                        logger.warning(f"Error reading {py_file}: {e}")

    def _audit_configuration_security(self):
        """Audit configuration files for security issues."""
        logger.info("⚙️ Auditing configuration security...")

        # Check Flask configuration
        try:
            config = get_config()
            if config.get("DEBUG", False):
                self.audit_results["high_issues"].append(
                    {
                        "tool": "manual",
                        "file": "app/config.py",
                        "issue": "Debug mode enabled",
                        "description": "Debug mode should be disabled in production",
                    }
                )
        except Exception as e:
            logger.warning(f"Could not load config: {e}")

        # Check environment files
        env_files = ["env.template", ".env", ".env.local"]
        for env_file in env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                with open(env_path, "r") as f:
                    content = f.read()

                # Check for hardcoded secrets
                if re.search(r"=.*[a-zA-Z0-9]{20,}", content):
                    self.audit_results["medium_issues"].append(
                        {
                            "tool": "manual",
                            "file": env_file,
                            "issue": "Potential hardcoded secret",
                            "description": "Long value detected, ensure no secrets are committed",
                        }
                    )

    def _audit_infrastructure_security(self):
        """Audit Terraform infrastructure for security issues."""
        logger.info("🏗️ Auditing infrastructure security...")

        terraform_dir = self.project_root / "terraform"
        if terraform_dir.exists():
            # Check main.tf for security configurations
            main_tf = terraform_dir / "main.tf"
            if main_tf.exists():
                with open(main_tf, "r") as f:
                    content = f.read()

                # Check for security group configurations
                if "ingress" in content and "0.0.0.0/0" in content:
                    self.audit_results["high_issues"].append(
                        {
                            "tool": "manual",
                            "file": "terraform/main.tf",
                            "issue": "Open security group rule",
                            "description": "Security group allows access from 0.0.0.0/0",
                        }
                    )

                # Check for encryption settings
                if "encrypted" in content and "false" in content:
                    self.audit_results["medium_issues"].append(
                        {
                            "tool": "manual",
                            "file": "terraform/main.tf",
                            "issue": "Unencrypted storage",
                            "description": "Storage volumes should be encrypted",
                        }
                    )

    def _audit_file_permissions(self):
        """Audit file permissions for security issues."""
        logger.info("📁 Auditing file permissions...")

        critical_files = [
            "app/config.py",
            "terraform/terraform.tfvars",
            ".env",
            "requirements.txt",
        ]

        for file_path in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                stat = full_path.stat()
                mode = oct(stat.st_mode)[-3:]

                # Check if file is world-readable
                if int(mode[2]) > 4:
                    self.audit_results["medium_issues"].append(
                        {
                            "tool": "manual",
                            "file": file_path,
                            "issue": "Overly permissive file permissions",
                            "description": f"File permissions: {mode}, should be 644 or less",
                        }
                    )

    def _audit_secrets_exposure(self):
        """Audit for exposed secrets and sensitive information."""
        logger.info("🔐 Auditing for secrets exposure...")

        # Check for common secret patterns
        secret_patterns = [
            r"sk-[a-zA-Z0-9]{48}",
            r"pk_[a-zA-Z0-9]{48}",
            r"[a-zA-Z0-9]{40}",
            r"[a-zA-Z0-9]{32}",
        ]

        # Files to exclude from secret scanning
        exclude_patterns = ["*.pyc", "__pycache__", "venv", ".git", "node_modules"]

        for py_file in self.project_root.rglob("*.py"):
            # Skip excluded files
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                for pattern in secret_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1
                        self.audit_results["critical_issues"].append(
                            {
                                "tool": "manual",
                                "file": str(py_file.relative_to(self.project_root)),
                                "line": line_num,
                                "issue": "Potential secret exposure",
                                "description": f"Secret pattern detected: {match.group()[:10]}...",
                            }
                        )
            except Exception as e:
                logger.warning(f"Error reading {py_file}: {e}")

    def _calculate_security_score(self):
        """Calculate overall security score."""
        logger.info("📊 Calculating security score...")

        # Scoring weights
        weights = {"critical": 10, "high": 5, "medium": 2, "low": 1, "info": 0}

        # Calculate penalty points
        penalty = 0
        for severity, weight in weights.items():
            count = len(self.audit_results[f"{severity}_issues"])
            penalty += count * weight

        # Base score is 100, subtract penalties
        base_score = 100
        final_score = max(0, base_score - penalty)

        self.audit_results["overall_score"] = final_score

        # Assign grade
        if final_score >= 90:
            grade = "A"
        elif final_score >= 80:
            grade = "B"
        elif final_score >= 70:
            grade = "C"
        elif final_score >= 60:
            grade = "D"
        else:
            grade = "F"

        self.audit_results["grade"] = grade

    def _generate_recommendations(self):
        """Generate security recommendations based on findings."""
        logger.info("💡 Generating security recommendations...")

        recommendations = []

        # Critical issues
        if self.audit_results["critical_issues"]:
            recommendations.append(
                {
                    "priority": "CRITICAL",
                    "action": "Immediate action required",
                    "description": f"Address {len(self.audit_results['critical_issues'])} critical security issues before deployment",
                }
            )

        # High issues
        if self.audit_results["high_issues"]:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "action": "Address within 24 hours",
                    "description": f"Fix {len(self.audit_results['high_issues'])} high-priority security issues",
                }
            )

        # Medium issues
        if self.audit_results["medium_issues"]:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "action": "Address within 1 week",
                    "description": f"Review and fix {len(self.audit_results['medium_issues'])} medium-priority issues",
                }
            )

        # General recommendations
        if self.audit_results["overall_score"] < 80:
            recommendations.append(
                {
                    "priority": "GENERAL",
                    "action": "Security review required",
                    "description": "Conduct comprehensive security review before production deployment",
                }
            )

        # Add specific recommendations based on findings
        if any(
            "hardcoded" in str(issue)
            for issue in self.audit_results["high_issues"]
            + self.audit_results["critical_issues"]
        ):
            recommendations.append(
                {
                    "priority": "HIGH",
                    "action": "Implement secrets management",
                    "description": "Use environment variables or AWS Secrets Manager for sensitive data",
                }
            )

        if any(
            "permissions" in str(issue) for issue in self.audit_results["medium_issues"]
        ):
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "action": "Review file permissions",
                    "description": "Ensure sensitive files have appropriate permissions (644 or less)",
                }
            )

        self.audit_results["recommendations"] = recommendations

    def generate_report(self, output_file: str = None) -> str:
        """Generate a comprehensive security audit report."""
        if output_file is None:
            output_file = self.project_root / "docs" / "SECURITY_AUDIT_REPORT.md"

        report = f"""# Security Audit Report - Smart CloudOps AI

**Generated**: {self.audit_results['timestamp']}  
**Overall Security Score**: {self.audit_results['overall_score']}/100 ({self.audit_results.get('grade', 'N/A')})

## 🚨 Critical Issues ({len(self.audit_results['critical_issues'])})

"""

        for issue in self.audit_results["critical_issues"]:
            report += f"- **{issue['file']}:{issue.get('line', 'N/A')}** - {issue['issue']}\n  - {issue['description']}\n\n"

        report += f"""## ⚠️ High Priority Issues ({len(self.audit_results['high_issues'])})

"""

        for issue in self.audit_results["high_issues"]:
            report += f"- **{issue['file']}:{issue.get('line', 'N/A')}** - {issue['issue']}\n  - {issue['description']}\n\n"

        report += f"""## 🔶 Medium Priority Issues ({len(self.audit_results['medium_issues'])})

"""

        for issue in self.audit_results["medium_issues"]:
            report += f"- **{issue['file']}:{issue.get('line', 'N/A')}** - {issue['issue']}\n  - {issue['description']}\n\n"

        report += f"""## 📋 Recommendations

"""

        for rec in self.audit_results["recommendations"]:
            report += f"- **{rec['priority']}**: {rec['action']}\n  - {rec['description']}\n\n"

        report += f"""## 📊 Detailed Results

### Dependency Scan
```json
{json.dumps(self.audit_results['dependency_scan'], indent=2)}
```

### Code Security Scan
```json
{json.dumps(self.audit_results['code_scan'], indent=2)}
```

### Configuration Security
```json
{json.dumps(self.audit_results['config_scan'], indent=2)}
```

### Infrastructure Security
```json
{json.dumps(self.audit_results['infrastructure_scan'], indent=2)}
```

---

**Note**: This report was generated automatically. Please review all findings and address critical and high-priority issues before production deployment.
"""

        # Write report to file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(report)

        logger.info(f"Security audit report generated: {output_file}")
        return str(output_file)


def main():
    """Main function to run the security audit."""
    try:
        auditor = SecurityAuditor()
        results = auditor.run_comprehensive_audit()

        # Generate report
        report_path = auditor.generate_report()

        # Print summary
        print(f"\n🔒 Security Audit Complete!")
        print(
            f"📊 Overall Score: {results['overall_score']}/100 ({results.get('grade', 'N/A')})"
        )
        print(f"🚨 Critical Issues: {len(results['critical_issues'])}")
        print(f"⚠️ High Issues: {len(results['high_issues'])}")
        print(f"🔶 Medium Issues: {len(results['medium_issues'])}")
        print(f"📋 Report Generated: {report_path}")

        # Exit with error code if critical issues found
        if results["critical_issues"]:
            print(
                "\n❌ Critical security issues found. Please address before deployment."
            )
            sys.exit(1)
        elif results["high_issues"]:
            print("\n⚠️ High priority security issues found. Please address soon.")
            sys.exit(2)
        else:
            print("\n✅ No critical or high priority security issues found.")
            sys.exit(0)

    except Exception as e:
        logger.error(f"Security audit failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
