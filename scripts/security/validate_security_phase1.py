#!/usr/bin/env python3
"""
Security validation script for Phase 1 security hardening.
Checks for hardcoded secrets, weak configurations, and security issues.
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple

# Security patterns to detect
SECURITY_PATTERNS = {
    "hardcoded_passwords": [
        r'password\s*=\s*["\'][\w\d]{1,20}["\']',
        r'PASSWORD\s*=\s*["\'][\w\d]{1,20}["\']',
        r'admin:admin',
        r'default.*password',
        r'password.*:.*admin',
    ],
    "weak_secrets": [
        r'secret.*=\s*["\']\w{1,31}["\']',  # Secrets less than 32 chars
        r'SECRET_KEY\s*=\s*["\']\w{1,31}["\']',
        r'JWT.*KEY\s*=\s*["\']\w{1,31}["\']',
    ],
    "api_keys": [
        r'api[_-]?key\s*=\s*["\'][^$\{][^"\']*["\']',
        r'API[_-]?KEY\s*=\s*["\'][^$\{][^"\']*["\']',
        r'sk-[a-zA-Z0-9]{48}',  # OpenAI key pattern
    ],
    "aws_credentials": [
        r'AKIA[0-9A-Z]{16}',  # AWS Access Key ID
        r'aws_secret_access_key\s*=\s*["\'][^$\{]',
        r'AWS_SECRET_ACCESS_KEY\s*=\s*["\'][^$\{]',
    ]
}

# Files to exclude from scanning
EXCLUDE_PATTERNS = [
    "*.pyc", "*.pyo", "*.pyd", "__pycache__",
    "*.git", ".env", "venv", "node_modules",
    "*.log", "*.db", "*.sqlite",
    "requirements.lock", "package-lock.json",
    "*.min.js", "*.min.css"
]

# Files that should use environment variables
ENV_VAR_REQUIRED_FILES = [
    "docker-compose.yml",
    "docker-compose.*.yml",
    "values.yaml",
    "values-*.yaml",
    "*.tf",
    "*.tfvars.example"
]

class SecurityValidator:
    """Security validation for the codebase."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues = []
        self.warnings = []
        self.passed_checks = []
    
    def scan_file(self, filepath: Path) -> List[Dict]:
        """Scan a single file for security issues."""
        issues = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check each security pattern
            for pattern_type, patterns in SECURITY_PATTERNS.items():
                for pattern in patterns:
                    regex = re.compile(pattern, re.IGNORECASE)
                    
                    for line_num, line in enumerate(lines, 1):
                        if regex.search(line):
                            # Skip if it's a comment
                            if line.strip().startswith('#') or line.strip().startswith('//'):
                                continue
                            
                            # Skip if it's using environment variable
                            if '${' in line or 'os.environ' in line or 'getenv' in line:
                                continue
                            
                            issues.append({
                                "file": str(filepath.relative_to(self.project_root)),
                                "line": line_num,
                                "type": pattern_type,
                                "content": line.strip()[:100],  # Truncate long lines
                                "severity": "HIGH" if pattern_type in ["hardcoded_passwords", "api_keys", "aws_credentials"] else "MEDIUM"
                            })
        
        except Exception as e:
            print(f"Error scanning {filepath}: {e}")
        
        return issues
    
    def check_docker_security(self) -> List[Dict]:
        """Check Docker files for security issues."""
        issues = []
        dockerfiles = list(self.project_root.glob("**/Dockerfile*"))
        
        for dockerfile in dockerfiles:
            try:
                with open(dockerfile, 'r') as f:
                    content = f.read()
                    lines = content.splitlines()
                
                # Check for root user
                if not any("USER" in line and "root" not in line.lower() for line in lines):
                    issues.append({
                        "file": str(dockerfile.relative_to(self.project_root)),
                        "type": "docker_security",
                        "message": "Dockerfile should run as non-root user",
                        "severity": "HIGH"
                    })
                
                # Check for pinned base images
                from_lines = [line for line in lines if line.startswith("FROM")]
                for line in from_lines:
                    if "@sha256:" not in line and ":latest" not in line:
                        # Warning for non-pinned but versioned images
                        self.warnings.append({
                            "file": str(dockerfile.relative_to(self.project_root)),
                            "type": "docker_security",
                            "message": f"Consider pinning base image with SHA256 digest: {line}",
                            "severity": "LOW"
                        })
                    elif ":latest" in line:
                        issues.append({
                            "file": str(dockerfile.relative_to(self.project_root)),
                            "type": "docker_security",
                            "message": f"Don't use :latest tag in production: {line}",
                            "severity": "MEDIUM"
                        })
            
            except Exception as e:
                print(f"Error checking {dockerfile}: {e}")
        
        return issues
    
    def check_env_files(self) -> List[Dict]:
        """Check environment configuration files."""
        issues = []
        
        # Check if .env.example exists
        env_example = self.project_root / ".env.example"
        if not env_example.exists():
            issues.append({
                "type": "configuration",
                "message": "Missing .env.example file",
                "severity": "MEDIUM"
            })
        else:
            self.passed_checks.append("✅ .env.example file exists")
        
        # Check env.template for weak defaults
        env_template = self.project_root / "env.template"
        if env_template.exists():
            with open(env_template, 'r') as f:
                content = f.read()
            
            if "change-this" in content.lower() or "your-" in content.lower():
                self.warnings.append({
                    "file": "env.template",
                    "type": "configuration",
                    "message": "env.template may still contain placeholder values",
                    "severity": "LOW"
                })
        
        # Ensure .env is in .gitignore
        gitignore = self.project_root / ".gitignore"
        if gitignore.exists():
            with open(gitignore, 'r') as f:
                if ".env" in f.read():
                    self.passed_checks.append("✅ .env is in .gitignore")
                else:
                    issues.append({
                        "type": "configuration",
                        "message": ".env is not in .gitignore",
                        "severity": "CRITICAL"
                    })
        
        return issues
    
    def check_dependencies(self) -> List[Dict]:
        """Check dependency security."""
        issues = []
        
        requirements = self.project_root / "requirements.txt"
        requirements_lock = self.project_root / "requirements.lock"
        
        if requirements.exists():
            with open(requirements, 'r') as f:
                lines = f.readlines()
            
            # Check for unpinned dependencies
            unpinned = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '>=' in line and ',' not in line:  # >= without upper bound
                        unpinned.append(line)
            
            if unpinned:
                self.warnings.append({
                    "type": "dependencies",
                    "message": f"Found {len(unpinned)} dependencies without upper bounds",
                    "severity": "LOW",
                    "details": unpinned[:5]  # Show first 5
                })
        
        if not requirements_lock.exists():
            issues.append({
                "type": "dependencies",
                "message": "Missing requirements.lock with pinned hashes",
                "severity": "MEDIUM"
            })
        else:
            self.passed_checks.append("✅ requirements.lock exists")
        
        return issues
    
    def run_validation(self) -> Tuple[bool, Dict]:
        """Run all security validations."""
        
        print("🔍 Starting security validation...")
        
        # Scan Python files
        python_files = list(self.project_root.glob("**/*.py"))
        for filepath in python_files:
            # Skip excluded directories
            if any(exclude in str(filepath) for exclude in ["venv", "__pycache__", ".git", "node_modules"]):
                continue
            
            file_issues = self.scan_file(filepath)
            self.issues.extend(file_issues)
        
        # Scan configuration files
        config_files = (
            list(self.project_root.glob("**/*.yml")) +
            list(self.project_root.glob("**/*.yaml")) +
            list(self.project_root.glob("**/*.tf")) +
            list(self.project_root.glob("**/*.tfvars*"))
        )
        
        for filepath in config_files:
            if any(exclude in str(filepath) for exclude in ["venv", ".git", "node_modules"]):
                continue
            
            file_issues = self.scan_file(filepath)
            self.issues.extend(file_issues)
        
        # Run specific checks
        self.issues.extend(self.check_docker_security())
        self.issues.extend(self.check_env_files())
        self.issues.extend(self.check_dependencies())
        
        # Generate report
        report = {
            "total_issues": len(self.issues),
            "critical": len([i for i in self.issues if i.get("severity") == "CRITICAL"]),
            "high": len([i for i in self.issues if i.get("severity") == "HIGH"]),
            "medium": len([i for i in self.issues if i.get("severity") == "MEDIUM"]),
            "low": len([i for i in self.issues if i.get("severity") == "LOW"]),
            "warnings": len(self.warnings),
            "passed_checks": len(self.passed_checks),
            "issues": self.issues[:10],  # Show first 10 issues
            "warnings": self.warnings[:5],  # Show first 5 warnings
        }
        
        return len(self.issues) == 0, report

def main():
    """Main entry point."""
    
    project_root = Path(__file__).parent.parent.parent
    validator = SecurityValidator(project_root)
    
    print("=" * 60)
    print("🔐 SmartCloudOps AI - Security Validation (Phase 1)")
    print("=" * 60)
    
    passed, report = validator.run_validation()
    
    # Print passed checks
    if validator.passed_checks:
        print("\n✅ Passed Checks:")
        for check in validator.passed_checks:
            print(f"   {check}")
    
    # Print warnings
    if len(validator.warnings) > 0:
        print(f"\n⚠️  Warnings ({len(validator.warnings)} total):")
        for warning in validator.warnings[:5]:
            print(f"   - [{warning.get('severity', 'LOW')}] {warning.get('file', 'General')}: {warning['message']}")
    
    # Print issues
    if not passed:
        print(f"\n❌ Security Issues Found ({report['total_issues']} total):")
        print(f"   Critical: {report['critical']}")
        print(f"   High: {report['high']}")
        print(f"   Medium: {report['medium']}")
        print(f"   Low: {report['low']}")
        
        if report["issues"]:
            print("\n🔴 Top Issues:")
            for issue in report["issues"]:
                if "file" in issue and "line" in issue:
                    print(f"   [{issue['severity']}] {issue['file']}:{issue['line']} - {issue['type']}")
                    if "content" in issue:
                        print(f"      > {issue['content']}")
                else:
                    print(f"   [{issue['severity']}] {issue.get('file', 'General')}: {issue['message']}")
        
        print("\n💡 Recommendations:")
        print("   1. Replace all hardcoded passwords with environment variables")
        print("   2. Use secrets management (AWS Secrets Manager, HashiCorp Vault)")
        print("   3. Ensure all secrets are at least 32 characters")
        print("   4. Pin Docker base images with SHA256 digests")
        print("   5. Create requirements.lock with: python scripts/security/pin_dependencies.py")
        
        # Save detailed report
        report_file = project_root / "security_validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        sys.exit(1)
    else:
        print("\n✅ All security checks passed!")
        print("   Phase 1 security hardening is complete.")
    
    return 0

if __name__ == "__main__":
    exit(main())
